import atexit
from bson import ObjectId
from models.model import Model
from models.encrypt_model import EncryptModel
from flask_login import UserMixin, AnonymousUserMixin

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
        self.id = None
        self.username = "Guest"
    
    def get_id(self):
        return self.id
    
    def viewable_servers(self):
        # TODO: return the shared server 
        raise NotImplementedError


model = Model()

def on_exit():
    model.close()
atexit.register(on_exit)
model.connect()

encrypt = EncryptModel()