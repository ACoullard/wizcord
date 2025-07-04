import atexit
from bson import ObjectId
from models.model import Model
from models.encrypt_model import EncryptModel
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, username: str):
        self.id = user_id
        self.username = username

        self.viewable_servers = model.get_viewable_server_ids(ObjectId(user_id))

    def get_id(self):
        return self.id


model = Model()

def on_exit():
    model.close()
atexit.register(on_exit)
model.connect()

encrypt = EncryptModel()