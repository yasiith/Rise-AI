from flask import Flask
from flask_cors import CORS
from routes.user_routes import users_bp
from routes.task_routes import tasks_bp
from routes.chat_routes import chat_bp
from routes.updates import updates_bp
import db
import os

print("🟩 DEBUG: MONGODB_URI =", os.environ.get("MONGODB_URI"))
print("🟩 DEBUG: GEMINI_API_KEY =", os.environ.get("GEMINI_API_KEY"))
print("🟩 DEBUG: PORT =", os.environ.get("PORT"))

app = Flask(__name__)

# Update CORS configuration to explicitly include your frontend domain
CORS(app, 
     resources={r"/*": {"origins": ["http://localhost:3000", "https://rise-ai-frontend.onrender.com"]}}, 
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

# Add explicit CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://rise-ai-frontend.onrender.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
