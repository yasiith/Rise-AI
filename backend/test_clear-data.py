import requests
import json

BASE_URL = "http://localhost:5000"

def clear_and_test():
    """Clear existing data and run fresh tests"""
    print("🧹 Running Clean Tests...\n")
    
    # Test 1: Register fresh users
    print("🧪 Registering Fresh Users...")
    
    user_data = {
        "username": "alice_employee",
        "email": "alice@example.com",
        "role": "employee",
        "full_name": "Alice Employee"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=user_data)
    print(f"Alice Registration - Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Alice registered successfully")
    elif response.status_code == 409:
        print("ℹ️ Alice already exists")
    
    manager_data = {
        "username": "bob_manager",
        "email": "bob@example.com",
        "role": "manager", 
        "full_name": "Bob Manager"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=manager_data)
    print(f"Bob Registration - Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Bob registered successfully")
    elif response.status_code == 409:
        print("ℹ️ Bob already exists")
    
    print("-" * 50)
    
    # Test 2: Create task via API
    print("🧪 Creating Task via API...")
    task_data = {
        "employee_username": "alice_employee",
        "title": "Design new user interface",
        "description": "Create mockups and prototypes for the new user interface design",
        "priority": "high"
    }
    
    response = requests.post(f"{BASE_URL}/submit-task", json=task_data)
    print(f"Task Creation - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print("-" * 50)
    
    # Test 3: AI Chat with Alice
    print("🧪 Testing AI Chat with Alice...")
    chat_data = {
        "username": "alice_employee",
        "message": "Hello! Can you show me my tasks?"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    print(f"AI Chat - Status: {response.status_code}")
    if response.status_code == 200:
        ai_response = response.json()["response"]
        print(f"AI Response: {ai_response}")
    print("-" * 50)
    
    # Test 4: Create task via AI
    print("🧪 Creating Task via AI...")
    chat_data = {
        "username": "alice_employee",
        "message": "I need to create a task: Fix the login bug. It's urgent and needs immediate attention."
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    print(f"AI Task Creation - Status: {response.status_code}")
    if response.status_code == 200:
        ai_response = response.json()["response"]
        print(f"AI Response: {ai_response}")
    print("-" * 50)
    
    # Test 5: Manager statistics
    print("🧪 Testing Manager Statistics...")
    chat_data = {
        "username": "bob_manager",
        "message": "Show me team statistics and overview"
    }
    
    response = requests.post(f"{BASE_URL}/chat", json=chat_data)
    print(f"Manager Stats - Status: {response.status_code}")
    if response.status_code == 200:
        ai_response = response.json()["response"]
        print(f"AI Response: {ai_response}")
    print("-" * 50)
    
    # Test 6: Get all tasks
    print("🧪 Getting All Tasks...")
    response = requests.get(f"{BASE_URL}/tasks")
    print(f"Get Tasks - Status: {response.status_code}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Total tasks found: {len(tasks)}")
        for task in tasks[:2]:  # Show first 2 tasks
            print(f"  - {task.get('title', 'No title')} ({task.get('status', 'No status')})")
    
    print("\n🎉 Clean tests completed!")

if __name__ == "__main__":
    clear_and_test()