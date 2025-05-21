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


client = MongoClient(DB_HOSTNAME, DB_PORT, username="admin", password="password")

db = client[DB_NAME]

messages_db = db[MESSAGES_COLLECTION_NAME]


messages_db.insert_one({"content": "hello world", "author": "user2"})

all_message = messages_db.find()

for message in all_message:
    print(message)



client.close()