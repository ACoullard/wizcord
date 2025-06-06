from pymongo import MongoClient

from pymongo.collection import Collection

import atexit
from datetime import datetime
from enum import Enum
from bson.objectid import ObjectId

from typing import Optional

DB_HOSTNAME = "localhost"
DB_PORT = 27017

DB_NAME = "wizcord"
MESSAGES_COLL_NAME = "messages"
SERVERS_COLL_NAME = "servers"
CHANNELS_COLL_NAME = "channels"
USERS_COLL_NAME = "users"
ROLES_COLL_NAME = "roles"
SERVER_MEMBERS_COLL_NAME = "server_member"
CHANNEL_MEMBERS_COLL_NAME = "channel_members"

class AccessLevel(Enum):
    VIEW = 0
    POST = 1

"""

Collections:

users: {
    user: {
        "_id",
        "username"
        "email"
        ...
    }
}

roles: {
    role: {
        "name",
        ...
    
    }

}

servers: {
    server:{
        "id",
        "name",
        "roles" : [
            "role_id",
            "role_id"
        ]
    }
}

channel_members: {
    channel_member: {
        "user_id",
        "channel_id",
        "access_level",
        "add_date"
    }
    ...
}

server_members: {
    server_member: {
        "user_id",
        "server_id",
        "roles": [
            role_id,
            role_id
            ],
    }
    ...
}

channels: {
    channel: {
        "_id",
        "server_id",
        "name",
        "creation_date"
    }
    ...
}


messages:{
    message:{
        "id",
        "content",
        "author",
        "timestamp",
        "channel_id",
    }
}


"""


class Model:
    def __init__(self):
        pass

    def connect(self):
        self.client = MongoClient(
            DB_HOSTNAME,
            DB_PORT,
            username="admin",
            password="password",
            serverSelectionTimeoutMS=2000)
        print("opened pyMongo connection")
        atexit.register(self.close)
        
        self.db = self.client[DB_NAME]
        self.messages = self.db[MESSAGES_COLL_NAME]
        self.servers = self.db[SERVERS_COLL_NAME]
        self.channels = self.db[CHANNELS_COLL_NAME]
        self.users = self.db[USERS_COLL_NAME]
        self.roles = self.db[ROLES_COLL_NAME]
        self.server_members = self.db[SERVER_MEMBERS_COLL_NAME]
        self.channel_members = self.db[CHANNEL_MEMBERS_COLL_NAME]
    
    def save_message(self, author_id: int, channel_id: ObjectId, timestamp: datetime, content: str):
        result = self.messages.insert_one({
            "author_id": author_id,
            "channel_id": channel_id,
            "timestamp": timestamp,
            "content": content
        })
        return result.inserted_id
    
    def add_server(self, server_name: str):
        result = self.servers.insert_one({
            "name":server_name,
            "channels":[],
            "users":[],  
        })
        return result.inserted_id
    
    def add_channel(self, channel_name: str, server_id: Optional[ObjectId] = None):
        if server_id is not None:
            if self.servers.find_one({"_id": server_id}) is None:
                raise ValueError("given server id does not exist")
            
            result = self.channels.insert_one({
                "server_id": server_id,
                "name": channel_name
            })
        else:
            result = self.channels.insert_one({
                "name": channel_name
            })
            
        return result.inserted_id

    def get_messages_in_channel(self, channel_id: ObjectId):
        return list(self.messages.find({"channel_id":channel_id}))
    

    def add_user(self, username: str, email: str):
        result = self.users.insert_one({
            "username": username,
            "email": email
        })
        return result.inserted_id

    def get_user_by_username(self, username: str):
        """Gets a user's id via their username"""
        user = self.users.find_one({"username" : username})
        if user:
            return user["_id"]
        else:
            print(f"user {username} not found")
            return None

    def get_viewable_servers_ids(self, user_id: ObjectId):
        """Gets the servers a certain user has access to"""
        server_id_list = self.server_members.distinct("server_id", {"user_id":user_id})

        return server_id_list
    
    def get_server_by_id(self, server_id: ObjectId):
        server = self.servers.find_one({"_id":server_id})
        return server


    def add_user_to_server(self, user_id: ObjectId, server_id: ObjectId, roles: Optional[list[ObjectId]] = None):
        server = self.servers.find_one({"_id":server_id})
        if not server:
            raise ValueError(f"server id {server_id} does not exist") 
        user = self.users.find_one({"_id":user_id})
        if not user:
            raise ValueError(f"user id {user_id} does not exist")
        
        if roles is not None:
            if any([role_id not in server["roles"] for role_id in roles]):
                raise ValueError("Invalid role assigned")
        else:
            roles = []
        

        responce = self.server_members.insert_one({
            "user_id": user_id,
            "serverv_id": server_id,
            "roles": roles
        })

        if not responce.acknowledged:
            raise Exception("write to server members failed")

        return responce.inserted_id
    
    def user_is_server_member(self, user_id: ObjectId, server_id: ObjectId):
        server_membership = self.server_members.find_one({
            "user_id":user_id,
            "server_id":server_id
            })
        return server_membership is not None
    
    def add_user_to_channel(self, user_id: ObjectId, channel_id: ObjectId, access_level: AccessLevel):
        channel = self.channels.find_one({"_id":channel_id})
        if not channel:
            raise ValueError(f"server id {server_id} does not exist") 
        user = self.users.find_one({"_id":user_id})
        if not user:
            raise ValueError(f"user id {user_id} does not exist")
        

        if "server_id" in channel and not self.user_is_server_member(user_id, server_id):
            raise ValueError(f"user is not a member of the server ")

    def close(self):
        self.client.close()
        print("Closed pyMongo connection")




# messages_db.insert_one({"content": "hello world", "author": "user2"})

# all_message = messages_db.find()

# for message in all_message:
#     print(message)


if __name__ == "__main__":
    model = Model()
    model.connect()
    print(model.client.is_mongos)

    server_id = model.add_server("test server")
    channel_id = model.add_channel(server_id, "test channel 1")

    print(model.save_message(1, channel_id, datetime.now(), "test message test message"))
    print(model.get_messages_in_channel(channel_id))
    model.close()
