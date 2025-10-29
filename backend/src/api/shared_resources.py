import atexit
from bson import ObjectId
from models.model import Model
from models.encrypt_model import EncryptModel
from models.anonymous_username_builder import build_anonymous_username
from flask_login import UserMixin, AnonymousUserMixin
from uuid import uuid4

class User(UserMixin):
    def __init__(self, user_id, username: str):
        self.id = user_id
        self.username = username

    def get_id(self):
        return self.id
    
    def viewable_servers(self):
        return model.get_viewable_server_ids(ObjectId(self.id))

class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.username = build_anonymous_username()
        object_id = model.add_user(self.username, "NaN")
        self.id = str(object_id)
        model.add_user_to_shared_server(object_id)

    @property
    def is_active(self):
        return True

    def get_id(self):
        return self.id
    
    def viewable_servers(self):
        return model.get_shared_servers()


model = Model()

def on_exit():
    model.close()
atexit.register(on_exit)
model.connect()

encrypt = EncryptModel()