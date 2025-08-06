from datetime import datetime
from bson import ObjectId
from db import db

class Task:
    def __init__(self, employee_username, title, description, priority="medium", status="pending", assigned_manager=None):
        self.employee_username = employee_username
        self.title = title
        self.description = description
        self.priority = priority  # 'low', 'medium', 'high', 'urgent'
        self.status = status  # 'pending', 'in_progress', 'completed', 'cancelled'
        self.assigned_manager = assigned_manager
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.due_date = None
        self.completion_date = None
    
    def to_dict(self):
        return {
            "employee_username": self.employee_username,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_manager": self.assigned_manager,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "due_date": self.due_date,
            "completion_date": self.completion_date
        }
    
    @staticmethod
    def create_task(task_data):
        tasks_collection = db["tasks"]
        return tasks_collection.insert_one(task_data)
    
    @staticmethod
    def get_task_by_id(task_id):
        tasks_collection = db["tasks"]
        try:
            return tasks_collection.find_one({"_id": ObjectId(task_id)})
        except Exception:
            return None
    
    @staticmethod
    def get_tasks_by_user(username):
        tasks_collection = db["tasks"]
        return list(tasks_collection.find({"employee_username": username}, {"_id": 1}).sort("created_at", -1))
    
    @staticmethod
    def get_all_tasks():
        tasks_collection = db["tasks"]
        return list(tasks_collection.find({}, {"_id": 1}).sort("created_at", -1))
    
    @staticmethod
    def get_tasks_by_status(status):
        tasks_collection = db["tasks"]
        return list(tasks_collection.find({"status": status}, {"_id": 1}).sort("created_at", -1))
    
    @staticmethod
    def get_tasks_by_priority(priority):
        tasks_collection = db["tasks"]
        return list(tasks_collection.find({"priority": priority}, {"_id": 1}).sort("created_at", -1))
    
    @staticmethod
    def get_tasks_by_manager(manager_username):
        tasks_collection = db["tasks"]
        return list(tasks_collection.find({"assigned_manager": manager_username}, {"_id": 1}).sort("created_at", -1))
    
    @staticmethod
    def update_task_status(task_id, status, completion_date=None):
        tasks_collection = db["tasks"]
        update_data = {
            "status": status, 
            "updated_at": datetime.utcnow()
        }
        
        if status == "completed" and completion_date:
            update_data["completion_date"] = completion_date
        
        try:
            return tasks_collection.update_one(
                {"_id": ObjectId(task_id)}, 
                {"$set": update_data}
            )
        except Exception:
            return None
    
    @staticmethod
    def update_task(task_id, update_data):
        tasks_collection = db["tasks"]
        update_data["updated_at"] = datetime.utcnow()
        try:
            return tasks_collection.update_one(
                {"_id": ObjectId(task_id)}, 
                {"$set": update_data}
            )
        except Exception:
            return None
    
    @staticmethod
    def delete_task(task_id):
        tasks_collection = db["tasks"]
        try:
            return tasks_collection.delete_one({"_id": ObjectId(task_id)})
        except Exception:
            return None
    
    @staticmethod
    def assign_manager(task_id, manager_username):
        tasks_collection = db["tasks"]
        try:
            return tasks_collection.update_one(
                {"_id": ObjectId(task_id)}, 
                {"$set": {"assigned_manager": manager_username, "updated_at": datetime.utcnow()}}
            )
        except Exception:
            return None
    
    @staticmethod
    def get_task_statistics():
        tasks_collection = db["tasks"]
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        return list(tasks_collection.aggregate(pipeline))
    
    @staticmethod
    def get_user_task_statistics(username):
        tasks_collection = db["tasks"]
        pipeline = [
            {"$match": {"employee_username": username}},
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        return list(tasks_collection.aggregate(pipeline))