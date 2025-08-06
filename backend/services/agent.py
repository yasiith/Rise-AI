import os
import google.generativeai as genai
from datetime import datetime
import json
import re
from db import chat_history_collection, tasks_collection, users_collection, db
from models.task import Task
from models.user import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self):
        # Initialize Gemini client
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables")
            self.use_simulation = True
        else:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.use_simulation = False
        
        # Use chat_history_collection instead of chat_sessions_collection
        self.chat_history_collection = chat_history_collection
        
        self.system_prompt = """
        You are Rise AI, a helpful assistant for an employee task management system. 
        You help employees submit tasks, check task status, and assist managers with task overview.
        
        Available actions for employees:
        1. Create and submit new tasks
        2. Check their task status and history
        3. Update task progress
        4. Get productivity insights
        
        Available actions for managers:
        1. View all team tasks
        2. Assign tasks to employees
        3. Update task statuses
        4. Get team performance overview
        5. View task statistics
        
        When a user wants to create a task, extract:
        - Title (required)
        - Description (required) 
        - Priority (low/medium/high/urgent, default: medium)
        
        Always be professional, helpful, and concise. If you need more information, ask specific questions.
        """
    
    def process_message(self, message, username):
        """Process user message and return AI response"""
        try:
            # Get user context
            user = User.find_by_username(username)
            if not user:
                return "I'm sorry, I couldn't find your user information. Please try logging in again."
            
            # Get user's tasks for context
            user_tasks = Task.get_tasks_by_user(username)
            
            # Build context for AI
            context = self._build_context(user, user_tasks, message)
            
            # Get AI response
            ai_response = self._get_ai_response(context, message)
            
            # Save conversation to history
            self._save_conversation(username, message, ai_response)
            
            return ai_response
            
        except Exception as e:
            print(f"Error processing message: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    def _build_context(self, user, tasks, message):
        """Build context for AI including user info and tasks"""
        context = {
            "user": {
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            },
            "tasks": {
                "total": len(tasks),
                "pending": len([t for t in tasks if t.get("status") == "pending"]),
                "in_progress": len([t for t in tasks if t.get("status") == "in_progress"]),
                "completed": len([t for t in tasks if t.get("status") == "completed"])
            },
            "current_message": message
        }
        return context
    
    def _get_ai_response(self, context, message):
        """Get response from Gemini API or return simulated response"""
        try:
            # Build the prompt with context
            full_prompt = self._build_prompt_with_context(context, message)
            
            if self.use_simulation:
                print("Using simulated responses (Gemini API key not available)")
                return self._generate_simulated_response(context, message)
            
            # Use Gemini API
            response = self.model.generate_content(full_prompt)
            
            if response.text:
                return response.text.strip()
            else:
                print("Empty response from Gemini API")
                return self._generate_simulated_response(context, message)
            
        except Exception as e:
            print(f"Error getting Gemini response: {str(e)}")
            return self._generate_simulated_response(context, message)
    
    def _build_prompt_with_context(self, context, message):
        """Build a complete prompt with system instructions and context"""
        prompt = f"""{self.system_prompt}

Current User Information:
- Name: {context['user']['full_name']}
- Role: {context['user']['role']}
- Username: {context['user']['username']}

Current Task Summary:
- Total tasks: {context['tasks']['total']}
- Pending: {context['tasks']['pending']}
- In Progress: {context['tasks']['in_progress']}
- Completed: {context['tasks']['completed']}

User Message: {message}

Please respond as Rise AI, keeping the following guidelines in mind:
1. Be helpful, professional, and concise
2. If the user wants to create a task, ask for title, description, and priority
3. If they want to view tasks, provide relevant information based on their role
4. For statistics requests, provide appropriate data based on their role (managers see team data, employees see personal data)
5. Always offer to help with next steps

Response:"""
        
        return prompt
    
    def _generate_simulated_response(self, context, message):
        """Generate simulated AI responses for testing when Gemini API is not available"""
        message_lower = message.lower()
        
        if "hello" in message_lower or "hi" in message_lower or "hey" in message_lower:
            return f"Hello {context['user']['full_name']}! I'm Rise AI, your task management assistant. How can I help you today?"
        
        elif "task" in message_lower and ("show" in message_lower or "view" in message_lower or "list" in message_lower or "my" in message_lower):
            total = context['tasks']['total']
            pending = context['tasks']['pending']
            if total == 0:
                return "You don't have any tasks yet. Would you like me to help you create one? Just say 'create a new task' to get started!"
            else:
                return f"📋 **Your Task Summary:**\n\n• Total tasks: {total}\n• Pending: {pending}\n• In Progress: {context['tasks']['in_progress']}\n• Completed: {context['tasks']['completed']}\n\nWould you like me to show you details of any specific tasks or help you create a new one?"
        
        elif "create" in message_lower and "task" in message_lower:
            return """🆕 **Let's create a new task!**

Please provide the following information:

**Required:**
• **Title:** Brief description of the task
• **Description:** Detailed explanation of what needs to be done

**Optional:**
• **Priority:** low, medium, high, or urgent (default: medium)

**Example:** 
"Create a task titled 'Review quarterly report' with high priority and description 'Review Q3 financial report and prepare summary for board meeting'"

What task would you like to create?"""
        
        elif "statistic" in message_lower or "stats" in message_lower or "analytics" in message_lower:
            if context['user']['role'] == 'manager':
                completion_rate = round((context['tasks']['completed'] / max(context['tasks']['total'], 1)) * 100, 1)
                return f"""📊 **Team Task Statistics:**

• **Total tasks:** {context['tasks']['total']}
• **Pending:** {context['tasks']['pending']}
• **In Progress:** {context['tasks']['in_progress']}
• **Completed:** {context['tasks']['completed']}
• **Completion rate:** {completion_rate}%

As a manager, you can also view individual team member statistics. Would you like me to show team performance details?"""
            else:
                completion_rate = round((context['tasks']['completed'] / max(context['tasks']['total'], 1)) * 100, 1)
                return f"""📊 **Your Personal Task Statistics:**

• **Total tasks:** {context['tasks']['total']}
• **Pending:** {context['tasks']['pending']}
• **In Progress:** {context['tasks']['in_progress']}
• **Completed:** {context['tasks']['completed']}
• **Personal completion rate:** {completion_rate}%

Keep up the great work! Would you like tips on improving your productivity?"""
        
        elif "help" in message_lower or "what can you do" in message_lower:
            if context['user']['role'] == 'manager':
                return """🤖 **I can help you with:**

**📋 Task Management:**
• "Show me all tasks" - View team tasks
• "Create a new task" - Add tasks for your team
• "Show task statistics" - Team performance overview
• "Assign task to [employee]" - Delegate tasks

**📊 Team Management:**
• "Show team performance" - Productivity insights
• "View employee tasks" - Individual task tracking
• "Generate reports" - Task completion reports

**💡 General:**
• Ask me anything about task management
• Get productivity tips and insights

What would you like to do?"""
            else:
                return """🤖 **I can help you with:**

**📋 Task Management:**
• "Show my tasks" - View your current tasks
• "Create a new task" - Add new tasks
• "Update task status" - Mark tasks as completed
• "Show my statistics" - Your productivity stats

**📊 Productivity:**
• Get insights about your work patterns
• Tips for better task management
• Progress tracking and motivation

**💡 General:**
• Ask me anything about task management
• Get help with organizing your work

What would you like to do today?"""
        
        elif "update" in message_lower and "status" in message_lower:
            return "📝 **Update Task Status**\n\nTo update a task status, please tell me:\n• Which task you want to update (by title or ID)\n• The new status (pending, in_progress, completed, cancelled)\n\nExample: 'Mark \"Review report\" as completed'\n\nWhich task would you like to update?"
        
        elif "thanks" in message_lower or "thank you" in message_lower:
            return f"You're welcome, {context['user']['full_name']}! I'm always here to help you manage your tasks efficiently. Is there anything else you'd like to do?"
        
        else:
            return f"""👋 **Hi {context['user']['full_name']}!**

I'm Rise AI, your personal task management assistant. I'm here to help you stay organized and productive!

**Quick actions you can try:**
• "Show my tasks" - View your current tasks
• "Create a new task" - Add a new task
• "Show statistics" - See your productivity stats
• "Help" - See all available commands

What would you like to do?"""
    
    def _save_conversation(self, username, user_message, ai_response):
        """Save conversation to chat history"""
        try:
            conversation = {
                "username": username,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow()
            }
            chat_history_collection.insert_one(conversation)
        except Exception as e:
            print(f"Error saving conversation: {str(e)}")
    
    def get_chat_history(self, username, limit=10):
        """Get chat history for a user"""
        try:
            history = list(
                chat_history_collection
                .find({"username": username}, {"_id": 0})
                .sort("timestamp", -1)
                .limit(limit)
            )
            return history
        except Exception as e:
            print(f"Error getting chat history: {str(e)}")
            return []
    
    def clear_chat_history(self, username):
        """Clear chat history for a user"""
        try:
            result = chat_history_collection.delete_many({"username": username})
            return result.deleted_count
        except Exception as e:
            print(f"Error clearing chat history: {str(e)}")
            return 0