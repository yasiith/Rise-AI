d/js/chat.js
class ChatApp {
    constructor() {
        this.messages = [];
        this.isTyping = false;
        this.sessionTimer = null;
        this.init();
    }

    init() {
        // Check if user is authenticated
        if (!auth.isLoggedIn()) {
            window.location.href = 'index.html';
            return;
        }

        this.initializeUI();
        this.attachEventListeners();
        this.startSessionTimer();
        this.loadChatHistory();
    }

    initializeUI() {
        const user = auth.getCurrentUser();
        
        // Set user info in header
        document.getElementById('userFullName').textContent = user.fullName;
        document.getElementById('userRole').textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);
        
        // Hide manager-only features for employees
        if (user.role !== 'manager') {
            const statsBtn = document.getElementById('quickStats');
            if (statsBtn) {
                statsBtn.style.display = 'none';
            }
        }

        // Focus on message input
        document.getElementById('messageInput').focus();
    }

    attachEventListeners() {
        // Chat form submission
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage();
        });

        // Logout button
        document.getElementById('logoutBtn').addEventListener('click', () => {
            this.logout();
        });

        // Quick action buttons
        document.getElementById('quickShowTasks').addEventListener('click', () => {
            this.sendQuickAction('show_tasks');
        });

        document.getElementById('quickCreateTask').addEventListener('click', () => {
            this.sendQuickAction('create_task');
        });

        document.getElementById('quickStats').addEventListener('click', () => {
            this.sendQuickAction('task_stats');
        });

        document.getElementById('quickHelp').addEventListener('click', () => {
            this.sendQuickAction('help');
        });

        document.getElementById('clearHistory').addEventListener('click', () => {
            this.clearChatHistory();
        });

        // Enter key to send message
        document.getElementById('messageInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Clear input and show user message
        messageInput.value = '';
        this.addMessage(message, 'user');
        this.showTypingIndicator();

        try {
            const user = auth.getCurrentUser();
            const response = await API.sendMessage(user.username, message);
            
            this.hideTypingIndicator();
            this.addMessage(response.response, 'ai');
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
        }
    }

    async sendQuickAction(action) {
        const actionMessages = {
            'show_tasks': 'Show me my tasks',
            'create_task': 'I want to create a new task',
            'task_stats': 'Show me task statistics',
            'help': 'How can you help me?'
        };

        const message = actionMessages[action];
        if (!message) return;

        this.addMessage(message, 'user');
        this.showTypingIndicator();

        try {
            const user = auth.getCurrentUser();
            const response = await API.quickAction(user.username, action);
            
            this.hideTypingIndicator();
            this.addMessage(response.response, 'ai');
            
        } catch (error) {
            console.error('Error with quick action:', error);
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'ai', true);
        }
    }

    addMessage(content, sender, isError = false) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        
        const timestamp = new Date();
        const timeString = Utils.formatTime(timestamp);

        if (sender === 'user') {
            messageDiv.className = 'flex justify-end';
            messageDiv.innerHTML = `
                <div class="max-w-3xl">
                    <div class="flex items-start space-x-3 justify-end">
                        <div>
                            <div class="bg-indigo-600 text-white rounded-lg p-3 shadow-sm">
                                <p>${Utils.escapeHtml(content)}</p>
                            </div>
                            <span class="text-xs text-gray-500 mt-1 block text-right">${timeString}</span>
                        </div>
                        <div class="h-8 w-8 bg-gray-400 rounded-full flex items-center justify-center">
                            <i class="fas fa-user text-white text-sm"></i>
                        </div>
                    </div>
                </div>
            `;
        } else {
            messageDiv.className = 'flex justify-start';
            const bgColor = isError ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200';
            const textColor = isError ? 'text-red-900' : 'text-gray-900';
            
            messageDiv.innerHTML = `
                <div class="max-w-3xl">
                    <div class="flex items-start space-x-3">
                        <div class="h-8 w-8 bg-indigo-600 rounded-full flex items-center justify-center">
                            <i class="fas fa-robot text-white text-sm"></i>
                        </div>
                        <div>
                            <div class="${bgColor} rounded-lg shadow-sm border p-3">
                                <div class="${textColor}">${this.formatAIResponse(content)}</div>
                            </div>
                            <span class="text-xs text-gray-500 mt-1 block">${timeString}</span>
                        </div>
                    </div>
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Store message
        this.messages.push({
            content,
            sender,
            timestamp,
            isError
        });
    }

    formatAIResponse(content) {
        // Convert markdown-like formatting to HTML
        let formatted = Utils.escapeHtml(content);
        
        // Bold text (**text**)
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Bullet points (- text)
        formatted = formatted.replace(/^- (.+)$/gm, '• $1');
        
        // Preserve line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }

    showTypingIndicator() {
        this.isTyping = true;
        document.getElementById('typingIndicator').classList.remove('hidden');
        document.getElementById('sendBtn').disabled = true;
    }

    hideTypingIndicator() {
        this.isTyping = false;
        document.getElementById('typingIndicator').classList.add('hidden');
        document.getElementById('sendBtn').disabled = false;
    }

    async loadChatHistory() {
        try {
            const user = auth.getCurrentUser();
            const history = await API.getChatHistory(user.username, 5);
            
            if (history.history && history.history.length > 0) {
                // Add a separator for history
                const chatMessages = document.getElementById('chatMessages');
                const separator = document.createElement('div');
                separator.className = 'text-center py-2';
                separator.innerHTML = '<span class="text-xs text-gray-400 bg-gray-100 px-3 py-1 rounded-full">Previous conversation</span>';
                chatMessages.appendChild(separator);
                
                // Add history messages (in reverse order since they come newest first)
                history.history.reverse().forEach(msg => {
                    this.addMessage(msg.user_message, 'user');
                    this.addMessage(msg.ai_response, 'ai');
                });
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    async clearChatHistory() {
        if (confirm('Are you sure you want to clear your chat history?')) {
            try {
                const user = auth.getCurrentUser();
                await API.clearChatHistory(user.username);
                
                // Clear UI
                const chatMessages = document.getElementById('chatMessages');
                chatMessages.innerHTML = `
                    <div class="flex justify-start">
                        <div class="max-w-3xl">
                            <div class="flex items-start space-x-3">
                                <div class="h-8 w-8 bg-indigo-600 rounded-full flex items-center justify-center">
                                    <i class="fas fa-robot text-white text-sm"></i>
                                </div>
                                <div>
                                    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-3">
                                        <p class="text-gray-900">Hello! I'm Rise AI, your task management assistant. How can I help you today?</p>
                                    </div>
                                    <span class="text-xs text-gray-500 mt-1 block">Just now</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                this.messages = [];
                
            } catch (error) {
                console.error('Error clearing chat history:', error);
                alert('Failed to clear chat history. Please try again.');
            }
        }
    }

    startSessionTimer() {
        this.sessionTimer = setInterval(() => {
            document.getElementById('sessionTime').textContent = auth.getSessionDuration();
        }, 1000);
    }

    logout() {
        if (confirm('Are you sure you want to logout?')) {
            if (this.sessionTimer) {
                clearInterval(this.sessionTimer);
            }
            auth.logout();
        }
    }
}

// Initialize chat app when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('chatMessages')) {
        new ChatApp();
    }
});