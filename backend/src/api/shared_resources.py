import atexit
import os
from bson import ObjectId
from models.model import Model
from models.encrypt_model import EncryptModel
from flask_login import UserMixin
import redis as redis_lib

class User(UserMixin):
    def __init__(self, user_id, username: str):
        self.id = user_id
        self.username = username

    def get_id(self):
        return self.id

    def viewable_servers(self):
        return model.get_viewable_server_ids(ObjectId(self.id))


model = Model()

def on_exit():
    model.close()
atexit.register(on_exit)
model.connect()

encrypt = EncryptModel()

redis_client = redis_lib.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://127.0.0.1:6379"),
    decode_responses=False
)