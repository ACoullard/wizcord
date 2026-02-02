from pymongo import MongoClient
from pymongo.cursor import Cursor

from datetime import datetime, timezone
from enum import Enum
from bson.objectid import ObjectId
from dataclasses import dataclass

import json
import os

DB_HOSTNAME = os.environ.get("MONGODB_HOSTNAME", "localhost")
DB_PORT = int(os.environ.get("MONGODB_PORT", "27017"))
DB_USERNAME = os.environ.get("MONGODB_USERNAME", "admin")
DB_PASSWORD = os.environ.get("MONGODB_PASSWORD", "password")

DB_NAME = os.environ.get("MONGODB_DATABASE", "wizcord")
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



@dataclass
class Message:
    id: ObjectId
    content: str
    author_id: ObjectId
    timestamp: datetime
    channel_id: ObjectId

    def str_dict_format(self):
        return json.dumps({
        "id" : str(self.id),
        "content" : self.content,
        "author_id" : str(self.author_id),
        "timestamp" : str(self.timestamp),
        "channel_id" : str(self.channel_id),
        })

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
        "hidden": bool
    }
}


"""


class Model:
    def __init__(self):
        pass

    def connect(self, verbose = True):
        self.client = MongoClient(
            DB_HOSTNAME,
            DB_PORT,
            username=DB_USERNAME,
            password=DB_PASSWORD,
            serverSelectionTimeoutMS=2000)
        if verbose:
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
    
    def add_message(self, author_id: ObjectId, channel_id: ObjectId, content: str, timestamp: None | datetime = None) -> ObjectId:
        if timestamp is None:
            timestamp = datetime.now(tz=timezone.utc)

        author_id = ObjectId(author_id)
        channel_id = ObjectId(channel_id)
            
        result = self.messages.insert_one({
            "author_id": author_id,
            "channel_id": channel_id,
            "timestamp": timestamp,
            "content": content,
            "hidden": False
        })
        return result.inserted_id
    
    def hide_message(self, message_id: ObjectId):
        """Hides a given message by altering its "hidden" attribute  
        Returns the number of modified documents (should be 1 or 0)"""
        result = self.messages.update_one(
            {"_id": message_id},
            {"$set": {"hidden": True}}
        )
        return result.modified_count
    
    def add_server(self, server_name: str):
        result = self.servers.insert_one({
            "name":server_name,
            "channels":[],
            "users":[],  
        })
        return result.inserted_id
    
    def add_channel(self, channel_name: str, server_id: None | ObjectId = None):
        creation_date = datetime.now(tz=timezone.utc)
        if self.servers.find_one({"_id": server_id}) is None:
            raise ValueError("given server id does not exist")
        
        result = self.channels.insert_one({
            "server_id": server_id,
            "name": channel_name,
            "creation_date": creation_date,
        })
            
        return result.inserted_id
    
    def add_user(self, username: str, email: str) -> ObjectId:
        result = self.users.insert_one({
            "username": username,
            "email": email
        })
        return result.inserted_id

    def get_messages_filtered(self, channel_id: ObjectId | None = None, user_id: ObjectId | None = None, show_hidden: bool = False):
        query = {}
        if channel_id is not None:
            query["channel_id"] = channel_id
        if user_id is not None:
            query["author_id"] = user_id
        if not show_hidden:
            query["hidden"] = False

        messages = self.messages.find(query)
        return messages


    def get_user_id_by_username(self, username: str):
        """Gets a user's id via their username"""
        user = self.users.find_one({"username" : username})
        if user:
            return user["_id"]
        else:
            print(f"user {username} not found")
            return None

    def get_viewable_server_ids(self, user_id: ObjectId):
        """Gets the server ids a certain user has access to"""
        server_id_list = self.server_members.distinct("server_id", {"user_id":user_id})

        return server_id_list
    
    # admin command
    def get_all_servers(self) -> Cursor:
        """Gets a list of all servers in the database"""
        server_list = self.servers.find({})
        return server_list
    
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
    
    # admin command
    def get_all_users(self) -> Cursor:
        """Gets a list of all users in the database"""
        user_list = self.users.find({})
        return user_list

    def get_channel_ids_by_server(self, server_id: ObjectId):
        channels = self.channels.find({"server_id":server_id},)
        return [channel["channel_id"] for channel in channels]
    
    def get_channels_data_by_server(self, server_id: ObjectId):
        channel_datas = self.channels.find({"server_id": server_id})
        return channel_datas
    
    def get_user_ids_in_server(self, server_id: ObjectId):
        members = self.server_members.find(
            {"server_id": server_id},
            {"_id": 1})
        return members
    
    def get_paginated_messages(self, channel_id: ObjectId, page_num: int = 1, page_size: int = 10, show_hidden: bool = False):

        get_count = [{ "$count": "totalCount" }]

        print("Page size", page_size, type(page_size))
        print("page num:", page_num, type(page_num))
        get_paginated = [
            { "$skip": page_num * page_size },
            { "$limit": page_size }
        ]

        match_stage = {"$match": {"channel_id": channel_id}}
        if not show_hidden:
            match_stage["$match"]["hidden"] = False

        pipeline = [
            match_stage,
            {
                "$sort": {"timestamp": -1}
            },
            {
                "$project": {"channel_id": 0}
            },
            {
                "$facet": {
                    "metadata": get_count,
                    "data": get_paginated,
                },
            }]
        
        result = self.messages.aggregate(pipeline)
        return result

    
    def get_server_users_public_data(self, server_id: ObjectId, stringify_ids = False):
        get_user_ids = {
            "$match": {"server_id": server_id},
        }

        public_user_data_pipeline = [
            {"$project": {
                "username": 1,
                "_id":0
            }}
        ]
        lookup_user_data = {
            "$lookup": {
                "from":"users",
                "localField": "user_id",
                "foreignField": "_id",
                "pipeline": public_user_data_pipeline,
                "as": "user_data"
            }
        }

        unwind_user_data = {
            "$unwind": "$user_data"
        }
        # isolate_user = {
        #     "$replaceRoot": {
        #         "newRoot": "$user_data"
        #     }
        # }
        merge_user_data = {
            "$replaceRoot": {
                "newRoot": {
                    "$mergeObjects": ["$$ROOT", "$user_data"]
                }
            }
        }
        clean_up_result = {
            "$project": {
                "user_data": 0,
                "_id": 0,
            }
        }

        rename_user_id = {
            "$set": {
                "id": "$user_id",
                "user_id": "$$REMOVE"
            }
        }

        stringify = {
            "$addFields": {
                "server_id": {"$toString": "$server_id"},
                "id": {"$toString": "$id"},
            }
        }

        pipeline = [
            get_user_ids,
            lookup_user_data,
            unwind_user_data,
            merge_user_data,
            clean_up_result,
            rename_user_id
        ]

        if stringify_ids:
            pipeline.append(stringify)

        user_data = self.server_members.aggregate(pipeline)
        return user_data
        

    def add_user_to_server(self, user_id: ObjectId, server_id: ObjectId, roles: None | list[ObjectId] = None):
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
    
    def channel_exists(self, channel_id: ObjectId):
        channel = self.channels.find_one({"_id": channel_id})
        return channel is not None
    

# Shared server stuff
    
    def get_shared_servers(self):
        shared_server = self.servers.find_one({"name":"Wizcord Shared Server"})

        if shared_server is None:
            shared_server_id = self.add_server("Wizcord Shared Server")
            self.add_channel("General", shared_server_id)
            print("Created shared server with id:", shared_server_id)
            shared_server = self.servers.find_one({"_id": shared_server_id})
       
        return [shared_server]
        
    def add_user_to_shared_server(self, user_id: ObjectId):
        shared_servers = self.get_shared_servers()
        for shared_server in shared_servers:
            shared_server_id = shared_server["_id"]
            if not self.user_is_server_member(user_id, shared_server_id):
                self.add_user_to_server(user_id, shared_server_id)
                print(f"Added user {user_id} to shared server")

    def close(self, verbose = True):
        self.client.close()
        if verbose:
            print("Closed pyMongo connection")




# messages_db.insert_one({"content": "hello world", "author": "user2"})

# all_message = messages_db.find()

# for message in all_message:
#     print(message)


def setup_test_db(model: Model):
    print(model.client.is_mongos)

    server_id = model.add_server("test server")
    channel_id = model.add_channel("test channel 1", server_id)
    channel_id2 = model.add_channel("test channel 2", server_id)

    
    user_1_id = model.add_user("jerma985", "j.erma@bingbong.com")
    model.add_user_to_server(user_1_id, server_id)
    model.add_user_to_channel(user_1_id, channel_id, AccessLevel.POST)
    model.add_user_to_channel(user_1_id, channel_id2, AccessLevel.POST)

    user_2_id = model.add_user("theFreak", "admin@goon.cave")
    model.add_user_to_server(user_2_id, server_id)
    model.add_user_to_channel(user_2_id, channel_id, AccessLevel.VIEW)


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


    server_id = viewable_servers[0]

    users = model.get_server_users_public_data(server_id, stringify_ids=True)

    print(list(users))
    # print("Servers:")
    # for id in viewable_servers:
    #     server = model.get_server_by_id(id)
    #     print(server["name"])
    #     channel_ids = model.get_channel_ids_by_server(id)
    #     print("\nchannels:")
    #     for c_id in channel_ids:
    #         print(model.get_channel_by_id(c_id)["name"])      
    #         channel_id = c_id      


    # message_result = model.add_message(user_1_id, channel_id, datetime.now(), "test message test message")
    # messages = model.get_messages_by_channel(channel_id)
    # print("\nMessages:")
    # for message in messages:
    #     author_username = model.get_user_by_id(message["author_id"])["username"]
    #     print(f"\"{message["content"]}\" by: {author_username}")


    model.close()
