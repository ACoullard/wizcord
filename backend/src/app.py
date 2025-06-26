import os
from flask import Flask
import flask_login
from flask_session import Session
from redis import Redis
from bson import ObjectId

from shared_resources import model, User

from api_bp import api_bp


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16).hex()


app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = Redis.from_url('redis://127.0.0.1:6379')
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = 60*60*3 # three hours in seconds
Session(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    object_id = ObjectId(user_id)

    user = model.get_user_by_id(object_id)
    return User(user_id, user["username"])

app.register_blueprint(api_bp)