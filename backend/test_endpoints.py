import requests
import json

BASE_URL = "http://localhost:5000"

def test_database_connection():
    """Test database connection"""
    print("🧪 Testing Database Connection...")
    
    try:
        response = requests.get(f"{BASE_URL}/test-db")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    print("🧪 Testing User Registration...")
    
    user_data = {
        "username": "john_doe",
        "email": "john@example.com",
        "role": "employee",
        "full_name": "John Doe"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ User registration failed: {e}")
        return False

def test_manager_registration():
    """Test manager registration"""
    print("🧪 Testing Manager Registration...")
    
    manager_data = {
        "username": "jane_manager",
        "email": "jane@example.com", 
        "role": "manager",
        "full_name": "Jane Manager"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=manager_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Manager registration failed: {e}")
        return False

def test_ai_chat():
    """Test AI chat functionality"""
    print("🧪 Testing AI Chat...")
    
    chat_data = {
        "username": "john_doe",
        "message": "Hello! Can you help me?"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ AI chat failed: {e}")
        return False

def test_task_creation_via_ai():
    """Test task creation through AI"""
    print("🧪 Testing Task Creation via AI...")
    
    chat_data = {
        "username": "john_doe",
        "message": "I need to create a task: Update the company website with new content. This is high priority."
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Task creation via AI failed: {e}")
        return False

def test_show_tasks_via_ai():
    """Test showing tasks through AI"""
    print("🧪 Testing Show Tasks via AI...")
    
    chat_data = {
        "username": "john_doe",
        "message": "Show me my tasks"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Show tasks via AI failed: {e}")
        return False

def test_manual_task_submission():
    """Test manual task submission"""
    print("🧪 Testing Manual Task Submission...")
    
    task_data = {
        "employee_username": "john_doe",
        "title": "Fix login bug",
        "description": "There's a bug in the login system that needs fixing",
        "priority": "urgent"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit-task", json=task_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ Manual task submission failed: {e}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting Complete Backend Testing...\n")
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server is running: {response.json()}")
        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure Flask app is running on http://localhost:5000")
        return
    
    tests = [
        test_database_connection,
        test_user_registration,
        test_manager_registration,
        test_manual_task_submission,
        test_ai_chat,
        test_task_creation_via_ai,
        test_show_tasks_via_ai
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your backend is working correctly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    run_all_tests()