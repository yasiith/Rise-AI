from flask import Blueprint, request, jsonify
from models.user import User
from db import users_collection

users_bp = Blueprint('users', __name__)

@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    required_fields = ["username", "email", "role", "full_name"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Check if user already exists
    if User.find_by_username(data["username"]):
        return jsonify({"error": "Username already exists"}), 409
    
    user = User(data["username"], data["email"], data["role"], data["full_name"])
    User.create_user(user.to_dict())
    
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
    
    # Remove _id from response
    user.pop('_id', None)
    return jsonify(user), 200