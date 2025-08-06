from flask import Flask
from flask_cors import CORS
from routes.user_routes import users_bp
from routes.task_routes import tasks_bp
from routes.chat_routes import chat_bp
from routes.updates import updates_bp

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Register blueprints
app.register_blueprint(users_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(updates_bp)

@app.route('/')
def health_check():
    return {"status": "Rise AI Backend is running!", "version": "1.0.0"}, 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
