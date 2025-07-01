from pymongo import MongoClient

from datetime import datetime, timezone
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
        "_id",
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
        "author_id",
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
        # atexit.register(self.close)
        
        self.db = self.client[DB_NAME]
        self.messages = self.db[MESSAGES_COLL_NAME]
        self.servers = self.db[SERVERS_COLL_NAME]
        self.channels = self.db[CHANNELS_COLL_NAME]
        self.users = self.db[USERS_COLL_NAME]
        self.roles = self.db[ROLES_COLL_NAME]
        self.server_members = self.db[SERVER_MEMBERS_COLL_NAME]
        self.channel_members = self.db[CHANNEL_MEMBERS_COLL_NAME]
    
    def add_message(self, author_id: ObjectId, channel_id: ObjectId, timestamp: Optional[datetime], content: str):
        if timestamp is None:
            timestamp = datetime.now(tz=timezone.utc)
            
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
    
    def add_user(self, username: str, email: str):
        result = self.users.insert_one({
            "username": username,
            "email": email
        })
        return result.inserted_id

    def get_messages_in_channel(self, channel_id: ObjectId):
        return list(self.messages.find({"channel_id":channel_id}))


    def get_user_id_by_username(self, username: str):
        """Gets a user's id via their username"""
        user = self.users.find_one({"username" : username})
        if user:
            return user["_id"]
        else:
            print(f"user {username} not found")
            return None

    def get_viewable_server_ids(self, user_id: ObjectId):
        """Gets the servers a certain user has access to"""
        server_id_list = self.server_members.distinct("server_id", {"user_id":user_id})

        return server_id_list
    
    def get_server_by_id(self, server_id: ObjectId):
        server = self.servers.find_one({"_id":server_id})
        if server is None:
            raise ValueError(f"No server exists by the id {server_id}")
        return server
    
    def get_channel_by_id(self, channel_id: ObjectId):
        channel = self.channels.find_one({"_id": channel_id})
        if channel is None:
            raise ValueError(f"No channel exists by the id {channel_id}")
        return channel
    
    def get_user_by_id(self, user_id: ObjectId):
        user = self.users.find_one({"_id": user_id})
        if user is None:
            raise ValueError(f"No user exists by the id {user_id}")
        return user
        

    def get_channel_ids_by_server(self, server_id: ObjectId):
        channels = self.channels.distinct("_id", {"server_id":server_id})
        return channels

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
            "server_id": server_id,
            "roles": roles
        })

        return responce.inserted_id
    
    def user_is_server_member(self, user_id: ObjectId, server_id: ObjectId):
        server_membership = self.server_members.find_one({
            "user_id":user_id,
            "server_id":server_id
            })
        return server_membership is not None
    
    def add_user_to_channel(self, user_id: ObjectId, channel_id: ObjectId, access_level: AccessLevel):

        if access_level not in AccessLevel:
            raise ValueError("invalid access level")
        
        channel = self.channels.find_one({"_id":channel_id})
        if not channel:
            raise ValueError(f"channel id {channel_id} does not exist") 
        user = self.users.find_one({"_id":user_id})
        if not user:
            raise ValueError(f"user id {user_id} does not exist")
        

        if "server_id" in channel:
            server_id = channel["server_id"]
            if not self.user_is_server_member(user_id, server_id):
                raise ValueError(f"user is not a member of the server")
        
        responce = self.channel_members.insert_one({
            "user_id":user_id,
            "channel_id":channel_id,
            "access_level":access_level.value,
            "add_date":datetime.now(tz=timezone.utc)
        })

        return responce.inserted_id

    def close(self):
        self.client.close()
        print("Closed pyMongo connection")




# messages_db.insert_one({"content": "hello world", "author": "user2"})

# all_message = messages_db.find()

# for message in all_message:
#     print(message)


def setup_test_db(model: Model):
    print(model.client.is_mongos)

    server_id = model.add_server("test server")
    channel_id = model.add_channel("test channel 1", server_id)
    
    user_1_id = model.add_user("jerma985", "j.erma@bingbong.com")
    model.add_user_to_server(user_1_id, server_id)
    model.add_user_to_channel(user_1_id, channel_id, AccessLevel.POST)


def drop_database(model: Model):
    model.client.drop_database(DB_NAME)

if __name__ == "__main__":
    model = Model()
    model.connect()

    drop_database(model)
    setup_test_db(model)

    user_1_id = model.get_user_id_by_username("jerma985")
    print("current user id:", user_1_id, type(user_1_id))
    
    viewable_servers = model.get_viewable_server_ids(user_1_id)

    print("Servers:")
    for id in viewable_servers:
        server = model.get_server_by_id(id)
        print(server["name"])
        channel_ids = model.get_channel_ids_by_server(id)
        print("\nchannels:")
        for c_id in channel_ids:
            print(model.get_channel_by_id(c_id)["name"])      
            channel_id = c_id      


    message_result = model.add_message(user_1_id, channel_id, datetime.now(), "test message test message")
    messages = model.get_messages_in_channel(channel_id)
    print("\nMessages:")
    for message in messages:
        author_username = model.get_user_by_id(message["author_id"])["username"]
        print(f"\"{message["content"]}\" by: {author_username}")


    model.close()
