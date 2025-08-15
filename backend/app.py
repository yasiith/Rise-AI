from flask import Flask
from flask_cors import CORS
from routes.user_routes import users_bp
from routes.task_routes import tasks_bp
from routes.chat_routes import chat_bp
from routes.updates import updates_bp
import db  # Import the whole module instead of specific functions
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
app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(updates_bp)

@app.route('/')
def health_check():
    return {"status": "Rise AI Backend is running!", "version": "1.0.0"}, 200

# MongoDB connection is likely handled inside the db module itself
# We don't need to explicitly test it here

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
