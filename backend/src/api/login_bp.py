from flask import Blueprint, request
from flask_login import login_user, current_user

from utils import make_responce
from .shared_resources import model, User, AnonymousUser

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
    result = login_user(AnonymousUser(), remember=True)
    if not result:
        return make_responce("Invalid login, user inactive", 401)
    else:
        print("success - logged in anonymous user", current_user.username, current_user.id)
        return  package_user_data(), 200

    
@login_bp.route("current-user")
def get_current_user():
    print("current user: ", current_user.username)
    if current_user.is_authenticated:
        return {"username":current_user.username, "id":current_user.id}, 200
    else:
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