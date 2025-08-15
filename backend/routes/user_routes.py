
from flask import Blueprint, request, jsonify
from models.user import User
from db import users_collection, db
import hashlib
import time
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route("/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        # ✅ Manual OPTIONS handling for credentials
        resp = jsonify(success=True)
        resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp, 204

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        email = data.get('email')
        password = data.get('password')
        print(f"Login attempt for email: {email}")

        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400

        user_data = users_collection.find_one({"email": email})
        if not user_data:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user_data.get('password_hash') != password_hash:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401

        user_response = {
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "role": user_data["role"]
        }

        token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
        print(f"Login successful for: {email}")

        # ✅ Set credentials + origin explicitly in response
        resp = jsonify({
            "success": True,
            "message": "Login successful",
            "user": user_response,
            "token": token
        })
        resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp, 200

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"success": False, "error": "An error occurred during login"}), 500


@users_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        print(f"Processing registration for: {data.get('email', 'unknown')}")
        print(f"Database: {db.name}, Collection: {users_collection.name}")

        required_fields = ['username', 'password', 'full_name', 'email', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400

        if users_collection.find_one({"email": data['email']}):
            return jsonify({"success": False, "error": "User with this email already exists"}), 409

        if users_collection.find_one({"username": data['username']}):
            return jsonify({"success": False, "error": "Username already taken"}), 409

        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        user_data = {
            "username": data['username'],
            "password_hash": password_hash,
            "full_name": data['full_name'],
            "email": data['email'],
            "role": data['role'],
            "created_at": datetime.utcnow()
        }

        result = users_collection.insert_one(user_data)
        if result.inserted_id:
            resp = jsonify({"success": True, "message": "User registered successfully"})
            resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
            resp.headers.add("Access-Control-Allow-Credentials", "true")
            return resp, 201
        else:
            return jsonify({"success": False, "error": "Failed to register user"}), 500

    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": "An error occurred during registration"}), 500


# 🔧 Test routes (optional — can be removed in production)
@users_bp.route("/test-password/<username>/<password>", methods=["GET"])
def test_password(username, password):
    try:
        user_data = users_collection.find_one({"username": username})
        if not user_data:
            return jsonify({"error": "User not found"}), 404

        stored_hash = user_data.get('password_hash', '')
        input_hash = hashlib.sha256(password.encode()).hexdigest()

        resp = jsonify({
            "username": username,
            "input_password": password,
            "input_hash": input_hash,
            "stored_hash": stored_hash,
            "match": input_hash == stored_hash,
            "common_passwords_test": {
                "password123": hashlib.sha256("password123".encode()).hexdigest() == stored_hash,
                "demo123": hashlib.sha256("demo123".encode()).hexdigest() == stored_hash,
                "employee123": hashlib.sha256("employee123".encode()).hexdigest() == stored_hash,
                "123456": hashlib.sha256("123456".encode()).hexdigest() == stored_hash
            }
        })
        resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/verify-db", methods=["GET"])
def verify_db():
    try:
        from db import client
        dbs = client.list_database_names()
        from db import db
        collections = db.list_collection_names()
        user_count = users_collection.count_documents({})
        test_id = users_collection.insert_one({"test": True, "timestamp": datetime.utcnow()}).inserted_id
        delete_result = users_collection.delete_one({"_id": test_id})

        resp = jsonify({
            "success": True,
            "connection": "Connected",
            "databases": dbs,
            "current_db": db.name,
            "collections": collections,
            "user_count": user_count,
            "test_insert": str(test_id),
            "test_delete": delete_result.deleted_count
        })
        resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp
    except Exception as e:
        import traceback
        resp = jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        resp.headers.add("Access-Control-Allow-Origin", "https://rise-ai-frontend.onrender.com")
        resp.headers.add("Access-Control-Allow-Credentials", "true")
        return resp, 500