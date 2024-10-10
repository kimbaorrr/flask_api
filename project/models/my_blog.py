import json
from project.models.db import connect
from bson.objectid import ObjectId
from project.models.log_error import constraint_error, system_error
import logging
class DuAn():
    def __init__(self):
        self.du_an_collection = None
        self.db_connect()
            
    def db_connect(self):
        self.du_an_collection = connect('my_blog', "du_an")
        
    def get(self):
        ds = self.du_an_collection.find()
        json_data = list(doc for doc in ds)
        json_data = json.dumps(json_data, default=str, ensure_ascii=False, indent=4)
        return json_data
    
    def update_viewer(self, oid):
        if not ObjectId.is_valid(oid):
            constraint_error('ID không tồn tại !')
        update_operation = {'$inc': {'viewer': 1}}
        self.du_an_collection.update_one({'_id': ObjectId(oid)}, update_operation)
            

class TienIch():
    def __init__(self):
        self.tien_ich_collection = None
        self.db_connect()
            
    def db_connect(self):
        self.tien_ich_collection = connect('my_blog', "tien_ich")
        
    def get(self):
        ds = self.tien_ich_collection.find()
        json_data = [doc for doc in ds]
        json_data = json.dumps(json_data, default=str, ensure_ascii=False, indent=4)
        return json_data
    
class PersonalInfo():
    def __init__(self):
        self.ttcn_collection = None
        self.db_connect()
            
    def db_connect(self):
        self.ttcn_collection = connect('my_blog', "personal_info")
        
    def get(self):
        ds = self.ttcn_collection.find()
        json_data = [doc for doc in ds]
        json_data = json.dumps(json_data, default=str, ensure_ascii=False, indent=4)
        return json_data
    
class AskQuestion():
    def __init__(self):
        self.ask_collection = None
        self.db_connect()
            
    def db_connect(self):
        self.ask_collection = connect('my_blog', "ask_question")
        
    def add(self, doc):
        try:
            self.ask_collection.insert_one(doc)
        except Exception as e:
            logging.error(f"Error in my_blog.AskQuestion: {str(e)}", exc_info=True)
            return system_error()
        
        