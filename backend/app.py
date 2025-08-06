from flask import Flask
from flask_cors import CORS
from routes.database import database_bp
from routes.updates import updates_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(database_bp)
app.register_blueprint(updates_bp)

@app.route("/")
def home():
    return {"message": "Rise AI Backend API", "status": "running"}

if __name__ == "__main__":
    app.run(debug=True)
