import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from db import users_collection, chat_history_collection, tasks_collection, updates_collection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print debug info
print(f"🟩 DEBUG: MONGODB_URI = {os.getenv('MONGODB_URI')}")
print(f"🟩 DEBUG: GEMINI_API_KEY = {os.getenv('GEMINI_API_KEY')}")
print(f"🟩 DEBUG: PORT = {os.getenv('PORT', '10000')}")

class AIAgent:
    """AI Agent powered by Google Generative AI (Gemini)"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.use_simulation = not self.api_key  # Use simulation if no API key is available
        
        if self.api_key:
            try:
                # Use Google Generative AI directly with correct implementation
                print("🔄 Initializing with Google Generative AI...")
                import google.generativeai as genai
                
                # Configure the API
                genai.configure(api_key=self.api_key)
                
                # List available models to see what's accessible with this API key
                print("📋 Checking available models...")
                available_models = genai.list_models()
                model_names = [model.name for model in available_models]
                print(f"📋 Available models: {model_names}")
                
                # Find a text model we can use
                text_model = None
                for model in available_models:
                    if "generateContent" in model.supported_generation_methods:
                        text_model = model.name
                        print(f"✅ Found usable text model: {text_model}")
                        break
                
                if not text_model:
                    # Fallback to a standard model name if we couldn't detect one
                    text_model = "gemini-pro"
                    print(f"⚠️ No text models found, trying default: {text_model}")
                
                # Initialize the model with the found model name
                self.model = genai.GenerativeModel(
                    model_name=text_model,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.95,
                    }
                )
                
                # Simple test
                print("🧪 Testing model with simple prompt...")
                test_response = self.model.generate_content("Hello")
                print(f"✅ Test successful, response: {test_response.text[:30]}...")
                
                self.use_simulation = False
                
            except Exception as e:
                print(f"❌ Error initializing Google Generative AI: {e}")
                import traceback
                print(traceback.format_exc())
                print("⚠️ Falling back to rule-based responses")
                self.use_simulation = True
        else:
            print("⚠️ No Gemini API key found, using simulation mode")

    def process_message(self, message: str, email: str) -> str:
        """Process a user message and return an AI response"""
        try:
            print(f"Processing message from {email}: {message}")
            
            user = users_collection.find_one({"email": email})
            if not user:
                return "I couldn't find your user account. Please try logging out and back in."
            
            user_role = user.get('role', 'employee')
            user_name = user.get('full_name', 'there')
            username = user.get('username', '')
            
            print(f"User: {user_name}, Role: {user_role}")
            
            chat_entry = {
                "username": email,
                "user_message": message,
                "timestamp": datetime.utcnow(),
            }

            # === DAILY UPDATE DETECTION & STORAGE (FOR EMPLOYEES ONLY) ===
            if user_role == "employee":
                update_keywords = ["worked on", "progress", "blocker", "done", "completed", "today", 
                                 "yesterday", "tomorrow", "task", "bug", "fix", "feature", "stuck", "help"]
                message_lower = message.lower()
                has_update_content = any(keyword in message_lower for keyword in update_keywords)
                is_long_enough = len(message.strip()) > 20

                if has_update_content and is_long_enough:
                    update_entry = {
                        "employee_username": username,
                        "employee_name": user_name,
                        "content": message.strip(),
                        "timestamp": datetime.utcnow()
                    }
                    try:
                        updates_collection.insert_one(update_entry)
                        print(f"✅ Daily update saved for {username}")
                        
                        success_msg = (
                            f"Got it, {user_name}! ✅\n\n"
                            "Your daily update has been successfully submitted.\n"
                            "Your manager will be able to view it in the updates section."
                        )
                        chat_entry["ai_response"] = success_msg
                        chat_history_collection.insert_one(chat_entry)
                        return success_msg

                    except Exception as e:
                        print(f"❌ Error saving update to DB: {e}")
                        error_msg = (
                            f"Thanks for sharing, {user_name}, but I couldn't submit your update right now. "
                            "Please try again later or use the app to submit it directly."
                        )
                        chat_entry["ai_response"] = error_msg
                        chat_history_collection.insert_one(chat_entry)
                        return error_msg

            # === MANAGER: NATURAL LANGUAGE HANDLING ===
            if user_role == "manager":
                message_lower = message.lower().strip()

                team_update_triggers = [
                    "recent updates", "latest updates", "team updates", "have there been",
                    "any new updates", "what have employees", "show me updates",
                    "daily reports", "status updates", "how is the team doing",
                    "team status", "all updates", "employee reports"
                ]
                if any(trigger in message_lower for trigger in team_update_triggers):
                    response = self._get_updates_summary(username, user_role)
                    chat_entry["ai_response"] = response
                    chat_history_collection.insert_one(chat_entry)
                    return response

                patterns = [
                    r"show me (\w+)'?s?\b",
                    r"updates? from (\w+)",
                    r"what did (\w+) (report|submit|work|do|update)",
                    r"how is (\w+) doing",
                    r"status of (\w+)",
                    r"(\w+)'?s\s+(update|progress|status)"
                ]
                reserved_keywords = {
                    "recent", "latest", "all", "team", "employee", "employees",
                    "any", "the", "my", "our", "this", "that", "new", "daily",
                    "status", "report", "update", "progress"
                }
                
                for pattern in patterns:
                    match = re.search(pattern, message_lower)
                    if match:
                        employee_name = match.group(1).lower()
                        if employee_name in reserved_keywords:
                            continue
                        response = self._get_employee_updates(username, employee_name)
                        chat_entry["ai_response"] = response
                        chat_history_collection.insert_one(chat_entry)
                        return response

            # === REGULAR AI RESPONSE GENERATION ===
            if self.use_simulation:
                response = self._generate_rule_based_response(message, user_role, user_name, username)
            else:
                if message.lower().startswith("/"):
                    response = self._process_command(message.lower(), username, user_role)
                else:
                    try:
                        # Create a system prompt
                        system_prompt = """You are Rise AI, an assistant for a task management system.

Your role is to help users submit daily updates (employees) or review team progress (managers).

Important rules:
1. NEVER invent or hallucinate updates, tasks, or user data.
2. If a user wants to submit a daily update, guide them to provide:
   - Tasks worked on today
   - Progress made
   - Blockers or challenges
   - Plans for tomorrow
3. For managers, if they ask for recent team updates (e.g., 'recent updates', 'team status'), summarize existing data.
4. If a manager asks about a specific employee (e.g., 'show me John's updates'), do NOT guess — rely on real data.
5. Always respond clearly and professionally."""

                        # Add context to guide AI behavior
                        contextual_message = (
                            f"{system_prompt}\n\n"
                            f"[USER: {user_name}, ROLE: {user_role}]\n"
                            f"IMPORTANT: If the manager asks for 'recent updates', 'team updates', or similar, "
                            f"fetch and summarize the latest employee updates using real data. "
                            f"If they mention a specific employee by name, only return that employee's updates. "
                            f"Do not invent anything.\n"
                            f"User message: {message}"
                        )
                        
                        # Using direct Gemini model instead of LangChain
                        response = self.model.generate_content(contextual_message).text
                        
                    except Exception as e:
                        print(f"⚠️ Error with Google Generative AI: {e}")
                        response = self._generate_rule_based_response(message, user_role, user_name, username)

            chat_entry["ai_response"] = response
            chat_history_collection.insert_one(chat_entry)
            return response

        except Exception as e:
            print(f"❌ Error in process_message: {e}")
            import traceback
            print(traceback.format_exc())
            return "I'm having trouble processing your request. Please try again later."

    def _process_command(self, command: str, username: str, role: str) -> str:
        """Process special slash commands"""
        if command.startswith("/tasks"):
            return self._get_tasks_summary(username, role)
        elif command.startswith("/updates"):
            parts = command.strip().split()
            if len(parts) > 1:
                target_employee = parts[1].strip().lower()
                if role == "manager":
                    return self._get_employee_updates(username, target_employee)
                else:
                    return "Only managers can view other employees' updates."
            return self._get_updates_summary(username, role)
        elif command.startswith("/help"):
            return self._get_help_message(role)
        else:
            return f"Unknown command '{command}'. Type /help for available commands."

    def _get_employee_updates(self, manager_username: str, employee_username: str) -> str:
        """Fetch updates from a specific employee (only if manager has access)"""
        try:
            employee = users_collection.find_one({
                "username": {"$regex": f"^{employee_username}$", "$options": "i"},
                "role": "employee"
            })
            if not employee:
                return f"Could not find an employee with username: {employee_username}"

            actual_username = employee["username"]
            updates = list(updates_collection.find({"employee_username": actual_username})
                           .sort("timestamp", -1).limit(5))
            if not updates:
                return f"{actual_username} hasn't submitted any updates yet."

            response = f"Recent updates from **{actual_username}**:\n\n"
            for update in updates:
                timestamp = update.get("timestamp")
                date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown date"
                content = update.get("content", "No content")
                response += f"📅 **{date_str}**:\n{content}\n\n"
            return response
        except Exception as e:
            print(f"Error fetching updates for {employee_username}: {e}")
            return f"Sorry, I couldn't retrieve updates for {employee_username} right now."

    def _get_tasks_summary(self, username: str, role: str) -> str:
        """Get summary of tasks for the user"""
        try:
            if role == "manager":
                tasks = list(tasks_collection.find({"assigned_manager": username}))
                if not tasks:
                    return "You haven't assigned any tasks yet."
                tasks_by_employee = {}
                for task in tasks:
                    emp = task.get("employee_username")
                    if emp not in tasks_by_employee:
                        tasks_by_employee[emp] = []
                    tasks_by_employee[emp].append(task)
                response = "Here's a summary of tasks you've assigned:\n\n"
                for emp, emp_tasks in tasks_by_employee.items():
                    response += f"**{emp}**:\n"
                    for task in emp_tasks:
                        status = task.get("status", "pending")
                        response += f"- {task.get('title')} ({status})\n"
                    response += "\n"
                return response
            else:
                tasks = list(tasks_collection.find({"employee_username": username}))
                if not tasks:
                    return "You don't have any assigned tasks yet."
                pending = [t for t in tasks if t.get("status") == "pending"]
                in_progress = [t for t in tasks if t.get("status") == "in-progress"]
                completed = [t for t in tasks if t.get("status") == "completed"]
                response = "Here's a summary of your tasks:\n\n"
                if pending:
                    response += "**Pending Tasks**:\n"
                    for task in pending:
                        response += f"- {task.get('title')}\n"
                    response += "\n"
                if in_progress:
                    response += "**In Progress**:\n"
                    for task in in_progress:
                        response += f"- {task.get('title')}\n"
                    response += "\n"
                if completed:
                    response += "**Completed**:\n"
                    for task in completed:
                        response += f"- {task.get('title')}\n"
                return response
        except Exception as e:
            print(f"Error in _get_tasks_summary: {e}")
            return "I encountered an error while fetching your tasks."

    def _get_updates_summary(self, username: str, role: str) -> str:
        """Get summary of recent updates"""
        try:
            if role == "manager":
                updates = list(updates_collection.find().sort("timestamp", -1).limit(10))
                if not updates:
                    return "There are no updates from your team yet."
                response = "Recent updates from your team:\n\n"
                for update in updates:
                    emp = update.get("employee_username", "Unknown")
                    timestamp = update.get("timestamp")
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown date"
                    content = update.get("content", "No content")
                    response += f"**{emp}** ({date_str}):\n{content}\n\n"
                return response
            else:
                updates = list(updates_collection.find({"employee_username": username})
                               .sort("timestamp", -1).limit(5))
                if not updates:
                    return "You haven't submitted any updates yet."
                response = "Your recent updates:\n\n"
                for update in updates:
                    timestamp = update.get("timestamp")
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown date"
                    content = update.get("content", "No content")
                    response += f"**{date_str}**:\n{content}\n\n"
                return response
        except Exception as e:
            print(f"Error in _get_updates_summary: {e}")
            return "I encountered an error while fetching updates."

    def _get_help_message(self, role: str) -> str:
        """Get help message based on user role"""
        common_commands = """
Available commands:
/tasks - View task summary
/updates - View recent updates
/help - Show this help message
"""
        if role == "manager":
            return "Manager Help:\n" + common_commands + """
You can also ask me:
- "Show me John's updates"
- "What did Alice report today?"
- "Show recent team updates"
- "How is the team doing?"
- "Status of David"
"""
        else:
            return "Employee Help:\n" + common_commands + """
You can also ask me:
- "Submit a daily update"
- "Show my task progress"
- "Help me prioritize my tasks"
"""

    def _generate_rule_based_response(self, message: str, role: str, name: str, username: str) -> str:
        """Generate a rule-based response when API is unavailable"""
        message = message.lower().strip()
        if any(greeting in message for greeting in ["hi", "hello", "hey"]):
            if role == "manager":
                return f"Hello {name}! I'm your management assistant. Ask about team or employee updates."
            else:
                return f"Hello {name}! Ready to submit your daily update?"

        update_triggers = ["update", "status", "progress", "done today", "worked on", "blocker"]
        if any(trigger in message for trigger in update_triggers):
            if role == "employee":
                return (f"Got it, {name}. Share:\n"
                        "1. Tasks worked on today\n"
                        "2. Progress\n"
                        "3. Blockers\n"
                        "4. Plans for tomorrow")
            else:
                return "Ask: 'Show me John's updates' or 'Recent team updates'."

        if any(word in message for word in ["task", "work", "project"]):
            return f"Use '/tasks' to view task assignments."

        if "help" in message:
            return self._get_help_message(role)

        if role == "manager":
            msg = message
            team_triggers = ["recent updates", "team updates", "any new", "what have employees"]
            if any(t in msg for t in team_triggers):
                return self._get_updates_summary(username, role)

            patterns = [r"show me (\w+)'?s?\b", r"updates? from (\w+)", r"how is (\w+) doing"]
            reserved = {"recent", "latest", "all", "team", "any", "new", "daily", "employee"}

            for pattern in patterns:
                match = re.search(pattern, msg)
                if match:
                    emp = match.group(1).lower()
                    if emp in reserved:
                        continue
                    return self._get_employee_updates(username, emp)

            return (f"Hi {name}, try:\n"
                    "- 'Show me Alex's updates'\n"
                    "- 'Recent team updates'")

        return f"Hi {name}, share what you worked on today."

    def get_chat_history(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get chat history for a specific user"""
        try:
            history = list(
                chat_history_collection.find(
                    {"username": username},
                    {"_id": 0, "username": 1, "user_message": 1, "ai_response": 1, "timestamp": 1}
                ).sort("timestamp", -1).limit(limit)
            )
            for entry in history:
                if "timestamp" in entry and isinstance(entry["timestamp"], datetime):
                    entry["timestamp"] = entry["timestamp"].isoformat()
            return history
        except Exception as e:
            print(f"Error in get_chat_history: {e}")
            return []

    def clear_chat_history(self, username: str) -> int:
        """Clear chat history for a specific user"""
        try:
            result = chat_history_collection.delete_many({"username": username})
            return result.deleted_count
        except Exception as e:
            print(f"Error in clear_chat_history: {e}")
            return 0