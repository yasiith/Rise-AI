import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection using environment variable
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["rise_ai_db"]  # Database name
updates_collection = db["updates"]  # Collection name

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