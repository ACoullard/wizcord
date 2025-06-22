from flask import Blueprint, request
from flask_login import login_user

from shared_resources import model

login_bp = Blueprint("login", __name__, url_prefix="login")

@login_bp.post("/")
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]

    # if verify_login(username, password):
    if verify_login_username_only(username):
        id = model.get_user_id_by_username(username)
        login_user(id)
    else:
        return 

def verify_login_username_only(username: str):
    user = model.get_user_id_by_username(username)
    if user is not None:
        return True
    else:
        return False
    
def verify_login(username: str, password: str):
    pass