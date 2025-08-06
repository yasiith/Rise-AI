from flask import Blueprint, request, jsonify
from services.agent import AIAgent

chat_bp = Blueprint('chat', __name__)
ai_agent = AIAgent()

@chat_bp.route("/chat", methods=["POST"])
def chat_with_ai():
    """Main chat endpoint for AI conversations"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("message") or not data.get("username"):
            return jsonify({
                "error": "Message and username are required"
            }), 400
        
        # Process the message with AI agent
        response = ai_agent.process_message(
            data["message"], 
            data["username"]
        )
        
        return jsonify({
            "response": response,
            "timestamp": data.get("timestamp"),
            "username": data["username"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Chat processing failed: {str(e)}"
        }), 500

@chat_bp.route("/chat/history/<username>", methods=["GET"])
def get_chat_history(username):
    """Get chat history for a specific user"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Validate limit
        if limit > 50:  # Prevent excessive data retrieval
            limit = 50
        
        history = ai_agent.get_chat_history(username, limit)
        
        return jsonify({
            "history": history,
            "count": len(history),
            "username": username
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to retrieve chat history: {str(e)}"
        }), 500

@chat_bp.route("/chat/history/<username>", methods=["DELETE"])
def clear_chat_history(username):
    """Clear chat history for a specific user"""
    try:
        deleted_count = ai_agent.clear_chat_history(username)
        
        return jsonify({
            "message": f"Cleared {deleted_count} chat messages",
            "deleted_count": deleted_count,
            "username": username
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to clear chat history: {str(e)}"
        }), 500

@chat_bp.route("/chat/quick-actions", methods=["POST"])
def quick_actions():
    """Handle quick action buttons (like 'Show my tasks', 'Create task')"""
    try:
        data = request.json
        
        if not data.get("action") or not data.get("username"):
            return jsonify({
                "error": "Action and username are required"
            }), 400
        
        # Map quick actions to messages
        action_messages = {
            "show_tasks": "Show me my tasks",
            "create_task": "I want to create a new task", 
            "task_stats": "Show me task statistics",
            "help": "How can you help me?"
        }
        
        action = data["action"]
        if action not in action_messages:
            return jsonify({
                "error": "Invalid action"
            }), 400
        
        # Process the quick action
        response = ai_agent.process_message(
            action_messages[action],
            data["username"]
        )
        
        return jsonify({
            "response": response,
            "action": action,
            "username": data["username"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Quick action failed: {str(e)}"
        }), 500

@chat_bp.route("/chat/status", methods=["GET"])
def chat_status():
    """Check if chat service is available"""
    try:
        # Simple health check
        return jsonify({
            "status": "active",
            "service": "Rise AI Chat",
            "version": "1.0.0"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500