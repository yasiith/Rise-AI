from flask import Blueprint, request, jsonify
from services.agent import AIAgent
from db import users_collection, chat_history_collection
from datetime import datetime
from flask_cors import cross_origin

# Initialize blueprint and AI agent
chat_bp = Blueprint('chat', __name__)
ai_agent = AIAgent()

# Notice we changed from "/" to this explicit path
@chat_bp.route("", methods=["POST", "OPTIONS"])
def chat():
    """Main chat endpoint for AI conversations"""
    if request.method == "OPTIONS":
        # Handle preflight request
        return "", 204
        
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        email = data.get('username')  # This is actually the email from frontend
        message = data.get('message')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        
        print(f"Chat request from {email}: {message}")
        
        if not email or not message:
            return jsonify({"success": False, "error": "Email and message are required"}), 400
        
        # Get the user record to provide context to AI
        user = users_collection.find_one({"email": email})
        if not user:
            print(f"User not found with email: {email}")
            return jsonify({
                "success": False,
                "error": "User not found",
                "response": "I don't recognize your user account. Please try logging out and back in.",
                "timestamp": timestamp
            }), 404
            
        try:
            # Get response from AI agent
            response = ai_agent.process_message(message, email)
            
            return jsonify({
                "success": True,
                "response": response,
                "timestamp": timestamp
            }), 200
            
        except Exception as agent_error:
            print(f"AI Agent error: {str(agent_error)}")
            import traceback
            print(traceback.format_exc())
            
            return jsonify({
                "success": False,
                "error": str(agent_error),
                "response": "I'm currently having trouble processing your request. Please try again later.",
                "timestamp": timestamp
            }), 500
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "Sorry, I encountered an error. Please try again.",
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@chat_bp.route("/history/<username>", methods=["GET"])
def get_chat_history(username):
    """Get chat history for a specific user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Find user by email
        user = users_collection.find_one({"email": username})
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
            
        history = ai_agent.get_chat_history(username, limit)
        
        return jsonify({
            "success": True,
            "history": history
        }), 200
        
    except Exception as e:
        print(f"Chat history error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route("/history/<username>", methods=["DELETE"])
def clear_chat_history(username):
    """Clear chat history for a specific user"""
    try:
        # Find user by email
        user = users_collection.find_one({"email": username})
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
            
        deleted_count = ai_agent.clear_chat_history(username)
        
        return jsonify({
            "success": True,
            "message": f"Deleted {deleted_count} messages"
        }), 200
        
    except Exception as e:
        print(f"Clear chat history error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route("/status", methods=["GET"])
def chat_status():
    """Check if chat service is available"""
    try:
        # Simple health check
        return jsonify({
            "success": True,
            "status": "Chat service is running",
            "ai_simulation": ai_agent.use_simulation,
            "api_key_configured": bool(ai_agent.api_key)
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500