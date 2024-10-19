from pymongo import MongoClient
import logging
import json
from project.models.common_handlers import system_error
def connect(db_name, db_collection_name):
    try:
        with open('db_connection_string.json', 'r') as f:
            connection_string = json.load(f)
        hostname = connection_string['hostname']
        port = connection_string['port']
        username = connection_string['username']
        password = connection_string['password']
        if username == '' or password == '':
            client = MongoClient(f'mongodb://{hostname}:{port}/')
        else:
            client = MongoClient(f'mongodb://{username}:{password}@{hostname}:{port}/')
        db = client[db_name]
        collection = db[db_collection_name]
        return collection
    except Exception as e:
        logging.error(f"Error in db.connect: {str(e)}", exc_info=True)
        system_error()