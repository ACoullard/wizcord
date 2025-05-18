from pymongo import MongoClient

DB_HOSTNAME = "localhost"
DB_PORT = 27017

DB_NAME = "wizcord"
MESSAGES_COLLECTION_NAME = "messages"


client = MongoClient(DB_HOSTNAME, DB_PORT)

db = client[DB_NAME]

messages_db = db[MESSAGES_COLLECTION_NAME]


messages_db.insert_one({"content": "hello world", "author": "user1"})

print(messages_db.find())



client.close()