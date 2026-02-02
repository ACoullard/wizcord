import os
from flask import Flask
import flask_login
from flask_session import Session
from flask_cors import CORS
from redis import Redis
from bson import ObjectId

from api.shared_resources import model, User, AnonymousUser

from api.api_bp import api_bp


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", os.urandom(16).hex())


app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = Redis.from_url(os.environ.get("REDIS_URL", 'redis://127.0.0.1:6379'))
app.config["SESSION_PERMANENT"] = True
# app.config["SESSION_COOKIE_SECURE"] = True # TODO: put this back to true in production
app.config["PERMANENT_SESSION_LIFETIME"] = 60*60*3 # three hours in seconds

Session(app)

login_manager = flask_login.LoginManager()
login_manager.anonymous_user = AnonymousUser
login_manager.init_app(app)

CORS(app, origins=[
    os.environ["FRONTEND_URL"]
],
supports_credentials=True)

@login_manager.user_loader
def load_user(user_id):
    print("user id", user_id)
    object_id = ObjectId(user_id)

    try:
        user = model.get_user_by_id(object_id)
        return User(user_id, user["username"])
    except Exception as e:
        print("Error loading user:", e)
        return None

app.register_blueprint(api_bp)

# Health check endpoint for Docker
@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200