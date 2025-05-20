from pymongo import MongoClient

DB_HOSTNAME = "localhost"
DB_PORT = 27017

DB_NAME = "wizcord"
MESSAGES_COLLECTION_NAME = "messages"


"""




"""


client = MongoClient(DB_HOSTNAME, DB_PORT, username="admin", password="password")

db = client[DB_NAME]

messages_db = db[MESSAGES_COLLECTION_NAME]


messages_db.insert_one({"content": "hello world", "author": "user2"})

all_message = messages_db.find()

for message in all_message:
    print(message)



client.close()