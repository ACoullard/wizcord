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
        "id",
        "username"
        "email"
        ...
    }
    user: {
        "id",
        ...
    }
}

servers: {
    server:{
        "id",
        "name",
        "users":{
            "user_id",
            "user_id"
        }
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

    def save_message(self, author_id: int, channel_id: ObjectId, timestamp: datetime, content: str):
        result = self.messages.insert_one({
            "author_id": author_id,
            "channel_id": channel_id,
            "timestamp": timestamp,
            "content": content
        })
        return result.inserted_id
    
    def add_new_server(self, server_name: str):
        result = self.servers.insert_one({
            "name":server_name,
            "channels":[],
            "users":[],  
        })
        return result.inserted_id
    
    def add_new_channel(self, server_id: ObjectId, channel_name: str):
        # TODO: Add handline for when server does not exist
        #
        result = self.servers.update_one(
            {"_id": server_id},
            {"$push": {"channels": channel_name}}
            )
        return result.upserted_id

    def get_messages_in_channel(self, channel_id: int):
        return list(self.messages.find({"channel_id":channel_id}))

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

    server_id = model.add_new_server("test server")
    channel_id = model.add_new_channel(server_id, "test channel 1")

    print(model.save_message(1, channel_id, datetime.now(), "test message test message"))
    print(model.get_messages_in_channel(channel_id))
    model.close()
