from models.user import User
from db import db

def create_demo_users():
    """Create demo users for testing"""
    
    # Demo Employee
    employee = User(
        username="demo_employee",
        email="employee@riseai.com",
        role="employee",
        full_name="Demo Employee",
        password="password123"
    )
    
    # Demo Manager
    manager = User(
        username="demo_manager",
        email="manager@riseai.com",
        role="manager",
        full_name="Demo Manager",
        password="password123"
    )
    
    # Check if users already exist
    if not User.find_by_username("demo_employee"):
        User.create_user(employee.to_dict(include_password=True))
        print("✅ Demo employee created")
    else:
        print("ℹ️ Demo employee already exists")
    
    if not User.find_by_username("demo_manager"):
        User.create_user(manager.to_dict(include_password=True))
        print("✅ Demo manager created")
    else:
        print("ℹ️ Demo manager already exists")

if __name__ == "__main__":
    create_demo_users()