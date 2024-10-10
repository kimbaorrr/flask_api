from pymongo import MongoClient
import logging

def connect(db_name, db_collection_name):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[db_collection_name]
        return collection
    except Exception as e:
        logging.error(f"Error in db.connect: {str(e)}", exc_info=True)