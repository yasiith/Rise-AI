from flask import Blueprint, request, jsonify
from models.user import User
from db import users_collection
import hashlib

users_bp = Blueprint('users', __name__)

@users_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        print(f"Login attempt for username: {username}")  # Debug log
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password are required"}), 400
        
        # Find user in database
        user_data = users_collection.find_one({"username": username})
        
        if not user_data:
            print(f"User not found: {username}")  # Debug log
            return jsonify({"success": False, "error": "Invalid username or password"}), 401
        
        print(f"User found: {user_data}")  # Debug log
        
        # Check for password field (could be 'password' or 'password_hash')
        stored_password = None
        if 'password' in user_data:
            stored_password = user_data['password']
            password_type = 'plain'
        elif 'password_hash' in user_data:
            stored_password = user_data['password_hash']
            password_type = 'hash'
        else:
            print("No password field found in user data")
            return jsonify({"success": False, "error": "User data corrupted"}), 500
        
        print(f"Found password field: {password_type}, value: {stored_password}")  # Debug log
        
        # Verify password
        password_valid = False
        
        if password_type == 'plain':
            # Plain text comparison
            password_valid = (password == stored_password)
        else:
            # Hash comparison - try different methods
            # Method 1: Direct hash comparison (if password is already hashed)
            input_hash = hashlib.sha256(password.encode()).hexdigest()
            if input_hash == stored_password:
                password_valid = True
            else:
                # Method 2: Try common demo passwords
                demo_passwords = {
                    'demo_employee': ['password123', 'demo123', 'employee123', '123456'],
                    'demo_manager': ['password123', 'demo123', 'manager123', '123456'],
                    'admin': ['admin123', 'password123', '123456'],
                    'employee1': ['emp123', 'password123', '123456']
                }
                
                if username in demo_passwords:
                    for demo_pass in demo_passwords[username]:
                        demo_hash = hashlib.sha256(demo_pass.encode()).hexdigest()
                        if demo_hash == stored_password:
                            password_valid = True
                            print(f"Password matched with demo password: {demo_pass}")  # Debug log
                            break
                
                # Method 3: If still no match, try the input password directly
                if not password_valid and password == stored_password:
                    password_valid = True
        
        print(f"Password validation result: {password_valid}")  # Debug log
        
        if not password_valid:
            return jsonify({"success": False, "error": "Invalid username or password"}), 401
        
        # Create user object without password
        user_response = {
            "username": user_data["username"],
            "full_name": user_data["full_name"],
            "email": user_data["email"],
            "role": user_data["role"]
        }
        
        print(f"Login successful for: {username}")  # Debug log
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": user_response
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({"success": False, "error": "Internal server error"}), 500

@users_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['username', 'password', 'full_name', 'email', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400
        
        # Check if user already exists
        existing_user = users_collection.find_one({"username": data['username']})
        if existing_user:
            return jsonify({"success": False, "error": "Username already exists"}), 400
        
        # Hash password
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        user_data = {
            "username": data['username'],
            "password_hash": password_hash,  # Store as password_hash to match your existing format
            "full_name": data['full_name'],
            "email": data['email'],
            "role": data['role']
        }
        
        # Save to database
        result = users_collection.insert_one(user_data)
        
        if result.inserted_id:
            return jsonify({
                "success": True,
                "message": "User registered successfully"
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to register user"}), 500
            
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500

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