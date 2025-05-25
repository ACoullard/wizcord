from pymongo import MongoClient

DB_HOSTNAME = "localhost"
DB_PORT = 27017

DB_NAME = "wizcord"
MESSAGES_COLLECTION_NAME = "messages"


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
        
        self.db = self.client[DB_NAME]
        self.messages = self.db[MESSAGES_COLLECTION_NAME]

    def save_message(self, author_id, channel_id, timestamp, content):
        self.messages.insert_one({
            "author_id": author_id,
            "channel_id": channel_id,
            "timestamp": timestamp,
            "content": content
        })

    def close(self):
        self.client.close()




# messages_db.insert_one({"content": "hello world", "author": "user2"})

# all_message = messages_db.find()

# for message in all_message:
#     print(message)


if __name__ == "__main__":
    model = Model()
    model.connect()
    print(model.client.is_mongos)
    model.close()
