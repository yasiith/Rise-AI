import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB URI from environment variables
mongo_uri = os.environ.get('MONGODB_URI')

if not mongo_uri:
    print("⚠️ No MONGODB_URI found, using local MongoDB")
    mongo_uri = "mongodb://localhost:27017/"

# Connect to MongoDB
try:
    client = MongoClient(mongo_uri)
    db = client["rise_ai_db"]
    print("✅ MongoDB connection successful!")
    
    # List available databases (for debugging)
    databases = client.list_database_names()
    print(f"📊 Available databases: {databases}")
    
    # List collections
    collections = db.list_collection_names()
    print(f"📁 Collections in rise_ai_db: {collections}")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

# Define collections
users_collection = db["users"]
tasks_collection = db["tasks"]
chat_history_collection = db["chat_sessions"]
updates_collection = db["updates"]