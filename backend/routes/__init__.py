from .user_routes import users_bp
from .task_routes import tasks_bp
from .chat_routes import chat_bp
from .updates import updates_bp

__all__ = [
    'users_bp',
    'tasks_bp',
    'chat_bp',
    'updates_bp'
]