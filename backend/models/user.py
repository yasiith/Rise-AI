from datetime import datetime
from db import db

class User:
    def __init__(self, username, email, role, full_name):
        self.username = username
        self.email = email
        self.role = role  # 'employee' or 'manager'
        self.full_name = full_name
        self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "created_at": self.created_at
        }
    
    @staticmethod
    def create_user(user_data):
        users_collection = db["users"]
        return users_collection.insert_one(user_data)
    
    @staticmethod
    def find_by_username(username):
        users_collection = db["users"]
        return users_collection.find_one({"username": username})
    
    @staticmethod
    def find_by_email(email):
        users_collection = db["users"]
        return users_collection.find_one({"email": email})
    
    @staticmethod
    def get_all_users():
        users_collection = db["users"]
        return list(users_collection.find({}, {"_id": 0}))
    
    @staticmethod
    def get_users_by_role(role):
        users_collection = db["users"]
        return list(users_collection.find({"role": role}, {"_id": 0}))
    
    @staticmethod
    def update_user(username, update_data):
        users_collection = db["users"]
        update_data["updated_at"] = datetime.utcnow()
        return users_collection.update_one(
            {"username": username}, 
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_user(username):
        users_collection = db["users"]
        return users_collection.delete_one({"username": username})