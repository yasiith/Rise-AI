import os
import google.generativeai as genai
from datetime import datetime
import json
import re
from db import db
from models.user import User
from models.task import Task

class AIAgent:
    def __init__(self):
        # Configure Gemini AI
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        # Use the working model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Get database collections
        self.chat_sessions_collection = db["chat_sessions"]
        
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
    
    def process_message(self, user_message, username):
        try:
            # Get user context
            user = User.find_by_username(username)
            if not user:
                return "User not found. Please register first."
            
            # Check if user wants to create a task
            if self._is_task_creation_request(user_message):
                return self._handle_task_creation(user_message, username, user)
            
            # Check if user wants task status
            elif self._is_task_status_request(user_message):
                return self._handle_task_status_request(username, user)
            
            # Check if user wants task statistics (for managers)
            elif self._is_statistics_request(user_message) and user['role'] == 'manager':
                return self._handle_statistics_request()
            
            # General conversation
            else:
                return self._handle_general_conversation(user_message, username, user)
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _is_task_creation_request(self, message):
        """Check if the user wants to create a task"""
        task_keywords = [
            'create task', 'new task', 'add task', 'submit task',
            'i need to', 'i have to', 'i want to create',
            'can you help me create', 'make a task'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in task_keywords)
    
    def _is_task_status_request(self, message):
        """Check if user wants to see task status"""
        status_keywords = [
            'my tasks', 'task status', 'show tasks', 'view tasks',
            'what are my tasks', 'task list', 'check tasks'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in status_keywords)
    
    def _is_statistics_request(self, message):
        """Check if user wants statistics"""
        stats_keywords = [
            'statistics', 'stats', 'overview', 'summary',
            'team performance', 'dashboard', 'analytics'
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in stats_keywords)  # Fixed: was status_keywords
    
    def _handle_task_creation(self, user_message, username, user):
        """Handle task creation requests"""
        try:
            # Try to extract task details from the message
            task_details = self._extract_task_details(user_message)
            
            if task_details['title'] and task_details['description']:
                # Create the task
                task = Task(
                    employee_username=username,
                    title=task_details['title'],
                    description=task_details['description'],
                    priority=task_details['priority']
                )
                
                result = Task.create_task(task.to_dict())
                
                if result.inserted_id:
                    response = f"""✅ Task created successfully!

**Task Details:**
- **Title:** {task_details['title']}
- **Description:** {task_details['description']}
- **Priority:** {task_details['priority']}
- **Status:** Pending

Your task has been submitted and is now visible to managers."""
                    
                    # Save the interaction
                    self.save_chat_session(username, user_message, response)
                    return response
                else:
                    return "Sorry, there was an error creating your task. Please try again."
            
            else:
                # Ask for missing details
                return self._ask_for_task_details(task_details)
                
        except Exception as e:
            return f"Error creating task: {str(e)}"
    
    def _extract_task_details(self, message):
        """Extract task details from user message using AI"""
        extraction_prompt = f"""
        Extract task details from this message: "{message}"
        
        Return a JSON object with:
        - title: string (main task title, if clear)
        - description: string (task description, if clear)  
        - priority: string (low/medium/high/urgent, default: medium)
        
        If title or description are not clear, set them as null.
        Only return valid JSON.
        """
        
        try:
            response = self.model.generate_content(extraction_prompt)
            # Try to parse JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                task_data = json.loads(json_match.group())
                return {
                    'title': task_data.get('title'),
                    'description': task_data.get('description'),
                    'priority': task_data.get('priority', 'medium')
                }
        except:
            pass
        
        # Fallback: return empty details
        return {'title': None, 'description': None, 'priority': 'medium'}
    
    def _ask_for_task_details(self, current_details):
        """Ask user for missing task details"""
        if not current_details['title']:
            return "I'd be happy to help you create a task! What's the title or main goal of your task?"
        elif not current_details['description']:
            return f"Great! I have the title: '{current_details['title']}'. Can you provide more details about what needs to be done?"
        else:
            return "Please provide both a title and description for your task."
    
    def _handle_task_status_request(self, username, user):
        """Handle requests to view task status"""
        try:
            user_tasks = Task.get_tasks_by_user(username)
            
            if not user_tasks:
                return "You don't have any tasks yet. Would you like to create one?"
            
            # Format tasks for display
            response = f"📋 **Your Tasks ({len(user_tasks)} total):**\n\n"
            
            for task in user_tasks[-5:]:  # Show last 5 tasks
                status_emoji = {
                    'pending': '🔄',
                    'in_progress': '⏳',
                    'completed': '✅',
                    'cancelled': '❌'
                }.get(task.get('status', 'pending'), '📝')  # Fixed: added .get() with default
                
                priority_emoji = {
                    'low': '🟢',
                    'medium': '🟡', 
                    'high': '🟠',
                    'urgent': '🔴'
                }.get(task.get('priority', 'medium'), '🟡')  # Fixed: added .get() with default
                
                response += f"{status_emoji} **{task.get('title', 'Untitled')}**\n"
                response += f"   {priority_emoji} Priority: {task.get('priority', 'medium').title()}\n"
                response += f"   📅 Created: {task.get('created_at', 'Unknown').strftime('%Y-%m-%d %H:%M') if isinstance(task.get('created_at'), datetime) else 'Unknown'}\n"
                response += f"   📊 Status: {task.get('status', 'pending').title()}\n\n"
            
            if len(user_tasks) > 5:
                response += f"... and {len(user_tasks) - 5} more tasks.\n\n"
            
            # Add task statistics
            stats = Task.get_user_task_statistics(username)
            if stats:
                response += "📊 **Your Task Summary:**\n"
                for stat in stats:
                    response += f"   {stat['_id'].title()}: {stat['count']}\n"
            
            self.save_chat_session(username, "Show my tasks", response)
            return response
            
        except Exception as e:
            return f"Error retrieving tasks: {str(e)}"
    
    def _handle_statistics_request(self):
        """Handle statistics requests for managers"""
        try:
            all_stats = Task.get_task_statistics()
            all_tasks = Task.get_all_tasks()
            
            response = "📊 **Team Task Overview:**\n\n"
            
            # Overall statistics
            total_tasks = len(all_tasks)
            response += f"📝 Total Tasks: {total_tasks}\n\n"
            
            if all_stats:
                response += "**Status Breakdown:**\n"
                for stat in all_stats:
                    percentage = round((stat['count'] / total_tasks) * 100, 1)
                    response += f"   {stat['_id'].title()}: {stat['count']} ({percentage}%)\n"
            
            # Recent tasks
            if all_tasks:
                response += "\n🕐 **Recent Tasks:**\n"
                for task in all_tasks[:3]:
                    response += f"   • {task.get('title', 'Untitled')} - {task.get('employee_username', 'Unknown')} ({task.get('status', 'pending')})\n"
            
            return response
            
        except Exception as e:
            return f"Error retrieving statistics: {str(e)}"
    
    def _handle_general_conversation(self, user_message, username, user):
        """Handle general conversation using AI"""
        try:
            # Get user's recent tasks for context
            user_tasks = Task.get_tasks_by_user(username)
            
            # Build context-aware prompt
            context = f"""
            User: {user['full_name']} ({user['role']})
            Active tasks: {len([t for t in user_tasks if t.get('status') in ['pending', 'in_progress']])}
            Total tasks: {len(user_tasks)}
            
            User message: {user_message}
            
            Respond helpfully. If they need task management help, guide them appropriately.
            """
            
            full_prompt = self.system_prompt + "\n\n" + context
            
            response = self.model.generate_content(full_prompt)
            ai_response = response.text
            
            # Save chat session
            self.save_chat_session(username, user_message, ai_response)
            
            return ai_response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def save_chat_session(self, username, user_message, ai_response):
        """Save chat interaction to database"""
        try:
            chat_data = {
                "username": username,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.utcnow()
            }
            self.chat_sessions_collection.insert_one(chat_data)
        except Exception as e:
            print(f"Error saving chat session: {e}")
    
    def get_chat_history(self, username, limit=10):
        """Get chat history for a user"""
        try:
            return list(self.chat_sessions_collection
                       .find({"username": username}, {"_id": 0})
                       .sort("timestamp", -1)
                       .limit(limit))
        except Exception as e:
            print(f"Error retrieving chat history: {e}")
            return []
    
    def clear_chat_history(self, username):
        """Clear chat history for a user"""
        try:
            result = self.chat_sessions_collection.delete_many({"username": username})
            return result.deleted_count
        except Exception as e:
            print(f"Error clearing chat history: {e}")
            return 0