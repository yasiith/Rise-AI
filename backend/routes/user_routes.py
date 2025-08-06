from flask import Blueprint, request, jsonify
from models.user import User
from db import users_collection

users_bp = Blueprint('users', __name__)

@users_bp.route("/login", methods=["POST"])
def login_user():
    """Authenticate user with username and password"""
    data = request.json
    
    if not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400
    
    # Authenticate user
    user = User.authenticate(data["username"], data["password"])
    
    if user:
        # Remove sensitive data and return user info
        user.pop('_id', None)
        return jsonify({
            "message": "Login successful",
            "user": user
        }), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@users_bp.route("/register", methods=["POST"])
def register_user():
    """Register new user (admin only - for backend creation)"""
    data = request.json
    required_fields = ["username", "email", "role", "full_name", "password"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    if User.find_by_username(data["username"]):
        return jsonify({"error": "Username already exists"}), 409
    
    if User.find_by_email(data["email"]):
        return jsonify({"error": "Email already exists"}), 409
    
    # Create user with password
    user = User(
        data["username"], 
        data["email"], 
        data["role"], 
        data["full_name"],
        data["password"]
    )
    
    User.create_user(user.to_dict(include_password=True))
    
    return jsonify({"message": "User registered successfully"}), 201

@users_bp.route("/users", methods=["GET"])
def get_all_users():
    users = User.get_all_users()
    return jsonify(users), 200

@users_bp.route("/users/<username>", methods=["GET"])
def get_user(username):
    user = User.find_by_username(username)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Remove sensitive data from response
    user.pop('_id', None)
    user.pop('password_hash', None)
    return jsonify(user), 200