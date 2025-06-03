from pymongo import MongoClient
import atexit
from datetime import datetime
from bson.objectid import ObjectId

DB_HOSTNAME = "localhost"
DB_PORT = 27017

DB_NAME = "wizcord"
MESSAGES_COLLECTION_NAME = "messages"
SERVERS_COLLECTION_NAME = "servers"
USERS_COLLECTION_NAME = "users"



"""

Collections:

users: {
    user: {
        "_id",
        "username"
        "email"
        ...
        "channels":
            ["channel_id", "access_level", "server_id"],
            ["channel_id", "access_level", "server_id"],
            ...
    }
    user: {
        "_id":,
        ...
    }
}

servers: {
    server:{
        "id",
        "name",
        "channels": {
            "channel": {
                "id",
                "name"
            }
        }
    }
}
TODO: Maybe add a channels collection? See if this would be more efficient


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
        self.messages = self.db[MESSAGES_COLLECTION_NAME]
        self.servers = self.db[SERVERS_COLLECTION_NAME]
        self.users = self.db[USERS_COLLECTION_NAME]

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
    
    def add_channel(self, server_id: ObjectId, channel_name: str):
        # TODO: Add handling for when server does not exist
        #
        result = self.servers.update_one(
            {"_id": server_id},
            {"$push": {"channels": channel_name}}
            )
        return result.upserted_id

    def get_messages_in_channel(self, channel_id: int):
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

    def get_viewable_servers(self, user_id: ObjectId):
        """Gets the servers a certain user has access to"""
        user = {"users": user_id}
        """
        option 1
        servers list stored in users, channel list stored in users
        get user obj -> return list

        add new server:
        go to all users who are a part, add them

        add new channel:
        add to channel list of all users who have -> add server to them if they don't have it


        option 2:
        channel list stored in users, server stored on channel
        got to user obj -> got to each channel
            note down its server

        add new server:
        
        option 3:
        channel list stored in users, channel list stored on server
        go to user obj -> go to each channel
            search for 
        
        """
        
        

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
