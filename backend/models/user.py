from datetime import datetime
from db import db
import hashlib

class User:
    def __init__(self, username, email, role, full_name, password=None):
        self.username = username
        self.email = email
        self.role = role  # 'employee' or 'manager'
        self.full_name = full_name
        self.password_hash = self._hash_password(password) if password else None
        self.created_at = datetime.utcnow()
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        if password:
            return hashlib.sha256(password.encode()).hexdigest()
        return None
    
    def verify_password(self, password):
        """Verify password against stored hash"""
        if not self.password_hash or not password:
            return False
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def to_dict(self, include_password=False):
        data = {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "full_name": self.full_name,
            "created_at": self.created_at
        }
        if include_password and self.password_hash:
            data["password_hash"] = self.password_hash
        return data
    
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
    def authenticate(username, password):
        """Authenticate user with username and password"""
        users_collection = db["users"]
        user_data = users_collection.find_one({"username": username})
        
        if not user_data:
            return None
        
        # Verify password
        if 'password_hash' in user_data:
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if user_data['password_hash'] == input_hash:
                # Remove password hash from returned data
                user_data.pop('password_hash', None)
                return user_data
        
        return None
    
    @staticmethod
    def get_all_users():
        users_collection = db["users"]
        return list(users_collection.find({}, {"_id": 0, "password_hash": 0}))
    
    @staticmethod
    def get_users_by_role(role):
        users_collection = db["users"]
        return list(users_collection.find({"role": role}, {"_id": 0, "password_hash": 0}))
    
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