import os
from flask import Flask, request, session
import flask_login
from flask_session import Session

from model import Model
from encrypt_model import EncryptModel

model = Model()
encrypt = EncryptModel()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16).hex()


Session(app)
login_manager = flask_login.LoginManager() 
login_manager.init_app(app)



class User:
    def __init__(self, user_id, username: str, anonymous = False):
        self.user_id = user_id
        self.is_active = True
        self.is_anonymous = anonymous
        self.is_authenticated = False

    def get_id(self):
        return self.user_id
    

@login_manager.user_loader
def load_user(user_id):
    user = model.get_user_by_id(user_id)
    return User(user_id, user["username"])

@app.route("/api/init_e2ee")
def init_e2ee():
    """Initializes the x25519 key exchange that starts the end 2 end encryption (E2EE).
    Returns the public key and signature while storing the private key in the session.
    """
    public_key, private_key, signature = encrypt.init_x25519_exchange()
    session["x255_private_key"] = private_key
    
    return {
        "x255_public_key":public_key.public_bytes_raw(),
        "signature":signature
    }


@app.route("/api/login", methods=["POST"])
def login():
    # login initializes a session
    # first publish 
    req = request.get_json()
