from flask import Flask
from flask_cors import CORS
from routes.user_routes import users_bp
from routes.task_routes import tasks_bp
from routes.chat_routes import chat_bp
from routes.updates import updates_bp
from db import test_connection
import os

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
if not test_connection():
    print("❌ WARNING: MongoDB connection failed. Check your connection and try again.")
    # You can uncomment the line below to exit if MongoDB isn't working
    # import sys; sys.exit(1)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
