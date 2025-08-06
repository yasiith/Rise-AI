from flask import Blueprint, jsonify
from db import client, db

database_bp = Blueprint('database', __name__)

@database_bp.route("/test-db", methods=["GET"])
def test_db():
    try:
        # Test connection
        client.admin.command('ping')
        
        # Get database info
        db_stats = db.command("dbstats")
        
        return jsonify({
            "status": "success",
            "message": "Database connection successful",
            "database": db_stats["db"],
            "collections": db.list_collection_names()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database connection failed: {str(e)}"
        }), 500