from flask import Blueprint, request, jsonify
from services.agent import AIAgent

chat_bp = Blueprint('chat', __name__)
ai_agent = AIAgent()

@chat_bp.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint for AI conversations"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        username = data.get('username')
        message = data.get('message')
        
        print(f"Chat request from {username}: {message}")  # Debug log
        
        if not username or not message:
            return jsonify({"success": False, "error": "Username and message are required"}), 400
        
        # Process message with AI agent
        response = ai_agent.process_message(message, username)
        
        print(f"AI response: {response}")  # Debug log
        
        return jsonify({
            "success": True,
            "response": response,
            "timestamp": data.get('timestamp')
        }), 200
        
    except Exception as e:
        print(f"Chat error: {str(e)}")  # Debug log
        return jsonify({"success": False, "error": "Internal server error"}), 500

@chat_bp.route("/chat/history/<username>", methods=["GET"])
def get_chat_history(username):
    """Get chat history for a specific user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        print(f"Getting chat history for {username}, limit: {limit}")  # Debug log
        
        history = ai_agent.get_chat_history(username, limit)
        
        return jsonify({
            "success": True,
            "history": history
        }), 200
        
    except Exception as e:
        print(f"Chat history error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route("/chat/history/<username>", methods=["DELETE"])
def clear_chat_history(username):
    """Clear chat history for a specific user"""
    try:
        deleted_count = ai_agent.clear_chat_history(username)
        
        return jsonify({
            "success": True,
            "message": f"Deleted {deleted_count} messages"
        }), 200
        
    except Exception as e:
        print(f"Clear chat history error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@chat_bp.route("/chat/status", methods=["GET"])
def chat_status():
    """Check if chat service is available"""
    try:
        # Simple health check
        return jsonify({
            "success": True,
            "status": "Chat service is running",
            "ai_simulation": ai_agent.use_simulation
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500