const API_BASE_URL = 'http://localhost:5000';

class API {
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Authentication
    static async login(credentials) {
        return this.request('/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    static async register(userData) {
        return this.request('/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    static async getUser(username) {
        return this.request(`/users/${username}`);
    }

    // Chat
    static async sendMessage(username, message) {
        return this.request('/chat', {
            method: 'POST',
            body: JSON.stringify({
                username: username,
                message: message,
                timestamp: new Date().toISOString()
            })
        });
    }

    static async getChatHistory(username, limit = 10) {
        return this.request(`/chat/history/${username}?limit=${limit}`);
    }

    static async clearChatHistory(username) {
        return this.request(`/chat/history/${username}`, {
            method: 'DELETE'
        });
    }

    static async quickAction(username, action) {
        return this.request('/chat/quick-actions', {
            method: 'POST',
            body: JSON.stringify({
                username: username,
                action: action
            })
        });
    }

    // Tasks
    static async submitTask(taskData) {
        return this.request('/submit-task', {
            method: 'POST',
            body: JSON.stringify(taskData)
        });
    }

    static async getAllTasks() {
        return this.request('/tasks');
    }

    static async getUserTasks(username) {
        return this.request(`/tasks/${username}`);
    }

    // Test endpoints
    static async testConnection() {
        return this.request('/');
    }

    static async testDatabase() {
        return this.request('/test-db');
    }
}

// Utility functions
const Utils = {
    formatTime(date) {
        return new Date(date).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },

    showMessage(element, message, type = 'info') {
        const colors = {
            success: 'bg-green-100 text-green-800 border-green-200',
            error: 'bg-red-100 text-red-800 border-red-200',
            info: 'bg-blue-100 text-blue-800 border-blue-200',
            warning: 'bg-yellow-100 text-yellow-800 border-yellow-200'
        };

        element.className = `p-4 rounded-md border ${colors[type] || colors.info}`;
        element.querySelector('#messageText').textContent = message;
        element.classList.remove('hidden');

        // Auto hide after 5 seconds
        setTimeout(() => {
            element.classList.add('hidden');
        }, 5000);
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};