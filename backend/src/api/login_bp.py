from flask import Blueprint, request
from flask_login import login_user, current_user

from utils import make_responce
from .shared_resources import model, User

login_bp = Blueprint("login", __name__, url_prefix="login")

@login_bp.post("")
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    print("username:", username)
    print("password:", password)
    # if verify_login(username, password):
    if verify_login_username_only(username):
        id = model.get_user_id_by_username(username)
        user = User(str(id), username)
        result = login_user(user, remember=True)
        if not result:
            return make_responce("Invalid login", 401)
        else:
            print("success")
            return make_responce("Successfully logged in", 200)
    else:
        return make_responce("Invalid login", 401)
    
@login_bp.route("current-user")
def get_current_user():
    if current_user.is_authenticated:
        return {"username":current_user.username, "id":current_user.id}, 200
    else:
        return {"username":None}, 200

def verify_login_username_only(username: str):
    user = model.get_user_id_by_username(username)
    if user is not None:
        return True
    else:
        return False
    
def verify_login(username: str, password: str):
    pass