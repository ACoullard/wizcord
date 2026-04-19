from flask import Blueprint, request
from flask_login import login_user, current_user

from utils import make_responce
from .shared_resources import model, User
from models.anonymous_username_builder import build_anonymous_username
from observers import server_members_observers

login_bp = Blueprint("login", __name__, url_prefix="login")

@login_bp.post("")
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    print("username:", username)
    print("password:", password)

    id = verify_login_username_only(username)

    # if verify_login(username, password):
    if id is not None:
        user_obj = User(str(id), username)
        result = login_user(user_obj, remember=True)
        if not result:
            return make_responce("Invalid login, user inactive", 401)
        else:
            print("success - logged in user", username, id)
            return package_user_data(), 200
    else:
        return make_responce("Invalid login", 401)

@login_bp.post("anonymous")
def login_anon():
    '''Logs in as a new anonymous user'''
    # Always create a new persistent anonymous user in DB and add to shared server(s).
    object_id, username = _create_and_publish_anonymous_user()

    user_obj = User(str(object_id), username)
    result = login_user(user_obj, remember=True)
    if not result:
        return make_responce("Invalid login, user inactive", 401)
    else:
        print("success - logged in anonymous user", current_user.username, current_user.id)
        return package_user_data(), 200

    
@login_bp.route("current-user")
def get_current_user():
    if current_user.is_authenticated:
        print("current user: ", current_user.username)
        return {"username":current_user.username, "id":current_user.id}, 200
    return make_responce("No authenticated user", 401)


def verify_login_username_only(username: str):
    '''Verifies that a user exists with that username.
    Returns the user's id if found, otherwise None.
    '''
    user_id = model.get_user_id_by_username(username)
    return user_id
    
def verify_login(username: str, password: str):
    pass

def package_user_data():
    return  {"username":current_user.username, "id":current_user.id}

def _create_and_publish_anonymous_user():
    """Create an anonymous DB user, add to shared server(s), and publish server-member events.
    Returns (object_id, username)
    """
    username = build_anonymous_username()
    object_id = model.add_user(username, "NaN", is_anonymous=True)
    model.add_user_to_shared_server(object_id)

    try:
        shared_servers = model.get_shared_servers()
        for shared_server in shared_servers:
            server_id_str = str(shared_server["_id"])
            observer = server_members_observers.get(server_id_str)
            if observer is not None:
                observer.publish(str(object_id), server_id_str, username)
    except Exception:
        # best effort publish; do not fail on publish errors
        pass

    return object_id, username
