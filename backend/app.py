from flask import Flask
from flask_cors import CORS
from routes.user_routes import users_bp
from routes.task_routes import tasks_bp
from routes.chat_routes import chat_bp
from routes.updates import updates_bp
from db import connect_to_mongodb  # Changed this import
import os

print("🟩 DEBUG: MONGODB_URI =", os.environ.get("MONGODB_URI"))
print("🟩 DEBUG: GEMINI_API_KEY =", os.environ.get("GEMINI_API_KEY"))
print("🟩 DEBUG: PORT =", os.environ.get("PORT"))

app = Flask(__name__)

# Update CORS configuration
cors_origins = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, 
     resources={r"/*": {"origins": cors_origins}}, 
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Register blueprints
app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(tasks_bp)
app.register_blueprint(chat_bp, url_prefix='/chat')  # Make sure this is /chat
app.register_blueprint(updates_bp)

@app.route('/')
def health_check():
    return {"status": "Rise AI Backend is running!", "version": "1.0.0"}, 200

# Test MongoDB connection on startup
try:
    # Attempt to connect to MongoDB
    db_client = connect_to_mongodb()
    print("✅ MongoDB connection successful!")
    print(f"📊 Available databases: {db_client.list_database_names()}")
    db = db_client.get_database('rise_ai_db')
    print(f"📁 Collections in rise_ai_db: {db.list_collection_names()}")
except Exception as e:
    print(f"❌ WARNING: MongoDB connection failed: {str(e)}")
    # You can uncomment the line below to exit if MongoDB isn't working
    # import sys; sys.exit(1)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
