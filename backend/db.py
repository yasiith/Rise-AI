import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection using environment variable
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URI)
db = client['rise_ai_db']  # Database name

# Collections
users_collection = db['users']
tasks_collection = db['tasks']
updates_collection = db['updates']
chat_history_collection = db['chat_history']  # Add this line
chat_sessions_collection = db['chat_sessions']  # Keep this for backward compatibility

# Test connection function
def test_connection():
    try:
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Test database access
        db_list = client.list_database_names()
        print(f"📊 Available databases: {db_list}")
        
        # Test collection access
        collections = db.list_collection_names()
        print(f"📁 Collections in rise_ai_db: {collections}")
        
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

# Test connection when module is imported
if __name__ == "__main__":
    test_connection()