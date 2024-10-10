from pymongo import MongoClient

def connect(db_name, db_collection_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db[db_collection_name]
    return collection