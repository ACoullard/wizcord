import os
from flask import Flask
import flask_login
from flask_session import Session
from redis import Redis
from shared_resources import model

from api_bp import api_bp

class User:
    def __init__(self, user_id, username: str, anonymous=False):
        self.id = user_id
        self.username = username
        self.is_active = True
        self.is_anonymous = anonymous
        self.is_authenticated = False

    def get_id(self):
        return self.id



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

app.register_blueprint(api_bp)


@login_manager.user_loader
def load_user(user_id):
    user = model.get_user_by_id(user_id)
    return User(user_id, user["username"])





