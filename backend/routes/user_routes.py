from flask_cors import cross_origin

from flask import Blueprint, request, jsonify
from models.user import User
from db import users_collection, db
import hashlib
import time
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin()
def login():
    if request.method == "OPTIONS":
        return "", 204
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for email: {email}")  # Debug log
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"}), 400
        
        # Find user in database by email instead of username
        user_data = users_collection.find_one({"email": email})
        
        if not user_data:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        # Verify password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user_data.get('password_hash') != password_hash:
            return jsonify({"success": False, "error": "Invalid email or password"}), 401
        
        # Create user object without password
        user_response = {
            "email": user_data["email"],
            "full_name": user_data["full_name"],
            "role": user_data["role"]
        }
        
        # Generate a simple token (in production, use JWT)
        token = hashlib.sha256(f"{email}{time.time()}".encode()).hexdigest()
        
        print(f"Login successful for: {email}")  # Debug log
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user_response,
            "token": token
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({"success": False, "error": "An error occurred during login"}), 500

@users_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Add detailed logging
        print(f"Processing registration for: {data.get('email', 'unknown')} with role: {data.get('role', 'unknown')}")
        print(f"Database being used: {db.name}, Collection: {users_collection.name}")
        
        # Validate required fields
        required_fields = ['username', 'password', 'full_name', 'email', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": data['email']})
        if existing_user:
            print(f"User with email {data['email']} already exists")
            return jsonify({"success": False, "error": "User with this email already exists"}), 409
        
        existing_username = users_collection.find_one({"username": data['username']})
        if existing_username:
            print(f"Username {data['username']} already taken")
            return jsonify({"success": False, "error": "Username already taken"}), 409
        
        # Hash password
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        # Create user document
        user_data = {
            "username": data['username'],
            "password_hash": password_hash,
            "full_name": data['full_name'],
            "email": data['email'],
            "role": data['role'],
            "created_at": datetime.utcnow()
        }
        
        # Debug print before insert
        print(f"Attempting to insert user: {user_data['username']}")
        
        # Insert user with explicit acknowledgment
        result = users_collection.insert_one(user_data)
        
        # Debug print after insert
        print(f"Insert result: {result.acknowledged}, ID: {result.inserted_id}")
        
        if result.inserted_id:
            return jsonify({"success": True, "message": "User registered successfully"}), 201
        else:
            return jsonify({"success": False, "error": "Failed to register user"}), 500
            
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"success": False, "error": "An error occurred during registration"}), 500

# Add a test route to help figure out the correct password
@users_bp.route("/test-password/<username>/<password>", methods=["GET"])
def test_password(username, password):
    """Test route to help figure out the correct password hash"""
    try:
        user_data = users_collection.find_one({"username": username})
        if not user_data:
            return jsonify({"error": "User not found"}), 404
        
        stored_hash = user_data.get('password_hash', '')
        input_hash = hashlib.sha256(password.encode()).hexdigest()
        
        return jsonify({
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@users_bp.route("/verify-db", methods=["GET"])
def verify_db():
    try:
        # Check connection
        from db import client
        dbs = client.list_database_names()
        
        # Check database
        from db import db
        collections = db.list_collection_names()
        
        # Count users
        user_count = users_collection.count_documents({})
        
        # Add a test document
        test_id = users_collection.insert_one({"test": True, "timestamp": datetime.utcnow()}).inserted_id
        
        # Delete the test document
        delete_result = users_collection.delete_one({"_id": test_id})
        
        return jsonify({
            "success": True,
            "connection": "Connected",
            "databases": dbs,
            "current_db": db.name,
            "collections": collections,
            "user_count": user_count,
            "test_insert": str(test_id),
            "test_delete": delete_result.deleted_count
        })
    except Exception as e:
        import traceback
        return jsonify({
            "success": False, 
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500