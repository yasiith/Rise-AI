from flask import Blueprint, request, jsonify
from db import updates_collection
from datetime import datetime

updates_bp = Blueprint('updates', __name__)

@updates_bp.route("/submit-update", methods=["POST"])
def submit_update():
    data = request.json
    if not data.get("employee_name") or not data.get("update_text"):
        return jsonify({"error": "Missing fields"}), 400

    # Add timestamp
    data["timestamp"] = datetime.utcnow()
    
    updates_collection.insert_one(data)
    return jsonify({"message": "Update saved successfully!"}), 201

@updates_bp.route("/get-updates", methods=["GET"])
def get_updates():
    updates = list(updates_collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(updates), 200