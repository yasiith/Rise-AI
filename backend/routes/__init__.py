from .database import database_bp
from .updates import updates_bp
from .user_routes import users_bp
from .task_routes import tasks_bp
from .chat_routes import chat_bp

__all__ = [
    'database_bp',
    'updates_bp', 
    'users_bp',
    'tasks_bp',
    'chat_bp'
]