from flask import Blueprint, request, jsonify
from models.task import Task
from models.user import User
from db import tasks_collection

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route("/submit-task", methods=["POST"])
def submit_task():
    data = request.json
    required_fields = ["employee_username", "title", "description"]
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Verify user exists
    user = User.find_by_username(data["employee_username"])
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    task = Task(
        data["employee_username"],
        data["title"],
        data["description"],
        data.get("priority", "medium")
    )
    
    Task.create_task(task.to_dict())
    return jsonify({"message": "Task submitted successfully"}), 201

@tasks_bp.route("/tasks", methods=["GET"])
def get_all_tasks():
    tasks = Task.get_all_tasks()
    return jsonify(tasks), 200

@tasks_bp.route("/tasks/<username>", methods=["GET"])
def get_user_tasks(username):
    tasks = Task.get_tasks_by_user(username)
    return jsonify(tasks), 200

@tasks_bp.route("/tasks/<task_id>/status", methods=["PUT"])
def update_task_status(task_id):
    data = request.json
    if "status" not in data:
        return jsonify({"error": "Status field required"}), 400
    
    from bson import ObjectId
    try:
        result = Task.update_task_status(ObjectId(task_id), data["status"])
        if result.modified_count:
            return jsonify({"message": "Task status updated"}), 200
        else:
            return jsonify({"error": "Task not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400