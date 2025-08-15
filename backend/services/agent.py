import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

from db import users_collection, chat_history_collection, tasks_collection, updates_collection
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    """AI Agent powered by LangChain and Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.use_simulation = not self.api_key  # Use simulation if no API key is available
        
        if self.api_key:
            try:
                # Initialize LangChain with Gemini model
                print("🔄 Initializing LangChain with Gemini...")
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-pro",
                    google_api_key=self.api_key,
                    temperature=0.7,
                    top_p=0.85,
                    top_k=40,
                    convert_system_message_to_human=True
                )
                
                # Create memory
                self.memory = ConversationBufferMemory()
                
                # Define system prompt with enhanced manager update detection
                template = """You are Rise AI, an assistant for a task management system.

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
5. Always respond clearly and professionally.

Current conversation:
{history}
Human: {input}
AI: """

                # Create conversation prompt
                prompt = PromptTemplate(input_variables=["history", "input"], template=template)
                
                # Create conversation chain
                self.conversation = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    prompt=prompt,
                    verbose=True
                )
                
                # Test connection
                print("✅ LangChain initialized with Gemini")
                self.use_simulation = False
                
            except Exception as e:
                print(f"❌ Error initializing LangChain: {e}")
                print("⚠️ Falling back to rule-based responses")
                self.use_simulation = True
        else:
            print("⚠️ No Gemini API key found, using simulation mode")
    
    def process_message(self, message: str, email: str) -> str:
        """Process a user message and return an AI response"""
        try:
            print(f"Processing message from {email}: {message}")
            
            # Get user from database
            user = users_collection.find_one({"email": email})
            if not user:
                return "I couldn't find your user account. Please try logging out and back in."
            
            user_role = user.get('role', 'employee')
            user_name = user.get('full_name', 'there')
            username = user.get('username', '')
            
            print(f"User: {user_name}, Role: {user_role}")
            
            # Store incoming message in chat history
            chat_entry = {
                "username": email,
                "user_message": message,
                "timestamp": datetime.utcnow(),
            }

            # === DAILY UPDATE DETECTION & STORAGE (FOR EMPLOYEES ONLY) ===
            if user_role == "employee":
                # Heuristic: check for update-like content
                update_keywords = ["worked on", "progress", "blocker", "done", "completed", "today", 
                                 "yesterday", "tomorrow", "task", "bug", "fix", "feature", "stuck", "help"]
                message_lower = message.lower()
                has_update_content = any(keyword in message_lower for keyword in update_keywords)
                is_long_enough = len(message.strip()) > 20  # Avoid capturing short messages like "ok"

                if has_update_content and is_long_enough:
                    # Prepare and save the update
                    update_entry = {
                        "employee_username": username,
                        "employee_name": user_name,
                        "content": message.strip(),
                        "timestamp": datetime.utcnow()
                    }
                    try:
                        updates_collection.insert_one(update_entry)
                        print(f"✅ Daily update saved for {username}")
                        
                        # Prepare success response
                        success_msg = (
                            f"Got it, {user_name}! ✅\n\n"
                            "Your daily update has been successfully submitted.\n"
                            "Your manager will be able to view it in the updates section."
                        )
                        chat_entry["ai_response"] = success_msg
                        chat_history_collection.insert_one(chat_entry)
                        return success_msg  # Exit early after submission

                    except Exception as e:
                        print(f"❌ Error saving update to DB: {e}")
                        error_msg = (
                            f"Thanks for sharing, {user_name}, but I couldn't submit your update right now. "
                            "Please try again later or use the app to submit it directly."
                        )
                        chat_entry["ai_response"] = error_msg
                        chat_history_collection.insert_one(chat_entry)
                        return error_msg

            # === MANAGER: NATURAL LANGUAGE HANDLING FOR TEAM & SPECIFIC EMPLOYEE UPDATES ===
            if user_role == "manager":
                message_lower = message.lower().strip()

                # 🟡 First: Detect general team updates BEFORE trying to parse employee names
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

                # 🟢 Now: Detect specific employee query (e.g., "Show me John's updates")
                patterns = [
                    r"show me (\w+)'?s?\b",
                    r"updates? from (\w+)",
                    r"what did (\w+) (report|submit|work|do|update)",
                    r"how is (\w+) doing",
                    r"status of (\w+)",
                    r"(\w+)'?s\s+(update|progress|status)"
                ]

                # List of words that should NEVER be treated as employee names
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
                            continue  # Skip if it's a keyword, not a real name
                        response = self._get_employee_updates(username, employee_name)
                        chat_entry["ai_response"] = response
                        chat_history_collection.insert_one(chat_entry)
                        return response

            # === REGULAR AI RESPONSE GENERATION (fallback) ===
            if self.use_simulation:
                response = self._generate_rule_based_response(message, user_role, user_name, username)  # Added username parameter
            else:
                if message.lower().startswith("/"):
                    response = self._process_command(message.lower(), username, user_role)
                else:
                    try:
                        # Add context to guide AI behavior
                        contextual_message = (
                            f"[USER: {user_name}, ROLE: {user_role}]\n"
                            f"IMPORTANT: If the manager asks for 'recent updates', 'team updates', or similar, "
                            f"fetch and summarize the latest employee updates using real data. "
                            f"If they mention a specific employee by name, only return that employee's updates. "
                            f"Do not invent anything.\n"
                            f"User message: {message}"
                        )
                        response = self.conversation.predict(input=contextual_message)
                    except Exception as e:
                        print(f"⚠️ Error with LangChain: {e}")
                        response = self._generate_rule_based_response(message, user_role, user_name, username)  # Added username

            # Store normal AI response
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
            # Extract optional employee username
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
            # Validate that this is a real employee
            employee = users_collection.find_one({
                "username": {"$regex": f"^{employee_username}$", "$options": "i"},  # Case-insensitive
                "role": "employee"
            })
            if not employee:
                return f"Could not find an employee with username: {employee_username}"

            actual_username = employee["username"]  # Use exact match

            updates = list(
                updates_collection.find({"employee_username": actual_username})
                .sort("timestamp", -1)
                .limit(5)
            )

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
                    return "You haven't assigned any tasks yet. You can create tasks for your team members."
                
                tasks_by_employee = {}
                for task in tasks:
                    employee = task.get("employee_username")
                    if employee not in tasks_by_employee:
                        tasks_by_employee[employee] = []
                    tasks_by_employee[employee].append(task)
                
                response = "Here's a summary of tasks you've assigned:\n\n"
                for employee, emp_tasks in tasks_by_employee.items():
                    response += f"**{employee}**:\n"
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
                    employee = update.get("employee_username", "Unknown")
                    timestamp = update.get("timestamp")
                    date_str = timestamp.strftime("%Y-%m-%d %H:%M") if timestamp else "Unknown date"
                    content = update.get("content", "No content")
                    response += f"**{employee}** ({date_str}):\n{content}\n\n"
                return response
            else:
                updates = list(updates_collection.find({"employee_username": username}).sort("timestamp", -1).limit(5))
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

        # Greeting responses
        if any(greeting in message for greeting in ["hi", "hello", "hey", "greetings"]):
            if role == "manager":
                return f"Hello {name}! I'm your management assistant. Ask about team or employee updates."
            else:
                return f"Hello {name}! Ready to submit your daily update?"

        # Update intent
        update_triggers = ["update", "status", "progress", "done today", "worked on", "blocker"]
        if any(trigger in message for trigger in update_triggers):
            if role == "employee":
                return (f"Got it, {name}. Share:\n"
                        "1. Tasks worked on today\n"
                        "2. Progress\n"
                        "3. Blockers\n"
                        "4. Plans for tomorrow")
            else:
                return (f"As a manager, ask: 'Show me John's updates' or 'Recent team updates'.");

        # Task-related
        if any(word in message for word in ["task", "work", "project"]):
            return f"Use '/tasks' to view task assignments."

        # Help
        if "help" in message:
            return self._get_help_message(role)

        # === MANAGER: Rule-based natural language handling ===
        if role == "manager":
            msg = message

            # Team updates first
            team_triggers = [
                "recent updates", "team updates", "any new", "what have employees",
                "show me updates", "daily reports", "how is the team doing"
            ]
            if any(t in msg for t in team_triggers):
                return self._get_updates_summary(username, role)  # Fixed: using username instead of name

            # Specific employee query
            patterns = [
                r"show me (\w+)'?s?\b", r"updates? from (\w+)", r"what did (\w+) (report|submit)",
                r"how is (\w+) doing", r"status of (\w+)", r"(\w+)'?s\s+update"
            ]
            reserved = {"recent", "latest", "all", "team", "any", "new", "daily", "employee", "employees"}

            for pattern in patterns:
                match = re.search(pattern, msg)
                if match:
                    emp = match.group(1).lower()
                    if emp in reserved:
                        continue
                    return self._get_employee_updates(username, emp)  # Fixed: using username instead of name

            return (f"Hi {name}, you can ask:\n"
                    "- 'Show me Alex's updates'\n"
                    "- 'Recent team updates'\n"
                    "- 'How is Sam doing?'")

        # Default employee
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