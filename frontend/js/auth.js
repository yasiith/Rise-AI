class Auth {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    init() {
        // Check if user is already logged in
        this.loadUserFromStorage();
        
        if (window.location.pathname.includes('chat.html') && !this.currentUser) {
            // Redirect to login if accessing chat without authentication
            window.location.href = 'index.html';
            return;
        }

        if (window.location.pathname.includes('index.html') || window.location.pathname === '/') {
            this.initLoginPage();
        }
    }

    initLoginPage() {
        // Get form elements
        const loginForm = document.getElementById('loginForm');
        const messageDiv = document.getElementById('messageDiv');
        const togglePassword = document.getElementById('togglePassword');
        const passwordInput = document.getElementById('password');
        const toggleIcon = document.getElementById('toggleIcon');

        // Password visibility toggle
        togglePassword?.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            if (type === 'password') {
                toggleIcon.className = 'fas fa-eye text-gray-400 hover:text-gray-600';
            } else {
                toggleIcon.className = 'fas fa-eye-slash text-gray-400 hover:text-gray-600';
            }
        });

        // Login form submission
        loginForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleLogin(e.target);
        });
    }

    async handleLogin(form) {
        const formData = new FormData(form);
        const credentials = {
            username: formData.get('username').trim(),
            password: formData.get('password')
        };
        
        const loginBtn = document.getElementById('loginBtn');
        const messageDiv = document.getElementById('messageDiv');

        if (!credentials.username || !credentials.password) {
            Utils.showMessage(messageDiv, 'Please fill in all fields', 'error');
            return;
        }

        // Show loading state
        loginBtn.disabled = true;
        loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Signing in...';

        try {
            // Authenticate with backend
            const response = await API.login(credentials);
            
            if (response.user) {
                // Successful login
                this.currentUser = {
                    username: response.user.username,
                    fullName: response.user.full_name,
                    email: response.user.email,
                    role: response.user.role
                };
                
                this.saveUserToStorage();
                Utils.showMessage(messageDiv, 'Login successful! Redirecting...', 'success');
                
                // Redirect to chat page
                setTimeout(() => {
                    window.location.href = 'chat.html';
                }, 1000);
                
            } else {
                Utils.showMessage(messageDiv, 'Invalid credentials', 'error');
            }
            
        } catch (error) {
            console.error('Login error:', error);
            
            if (error.message.includes('Invalid username or password')) {
                Utils.showMessage(messageDiv, 'Invalid username or password', 'error');
            } else {
                Utils.showMessage(messageDiv, 'Login failed. Please try again.', 'error');
            }
        } finally {
            // Reset button state
            loginBtn.disabled = false;
            loginBtn.innerHTML = '<span class="absolute left-0 inset-y-0 flex items-center pl-3"><i class="fas fa-sign-in-alt text-indigo-500 group-hover:text-indigo-400"></i></span>Sign in to Chat';
        }
    }

    saveUserToStorage() {
        if (this.currentUser) {
            localStorage.setItem('riseai_user', JSON.stringify(this.currentUser));
            localStorage.setItem('riseai_login_time', Date.now().toString());
        }
    }

    loadUserFromStorage() {
        const userData = localStorage.getItem('riseai_user');
        if (userData) {
            try {
                this.currentUser = JSON.parse(userData);
            } catch (error) {
                console.error('Error parsing user data:', error);
                this.logout();
            }
        }
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('riseai_user');
        localStorage.removeItem('riseai_login_time');
        window.location.href = 'index.html';
    }

    getCurrentUser() {
        return this.currentUser;
    }

    isLoggedIn() {
        return this.currentUser !== null;
    }

    getSessionDuration() {
        const loginTime = localStorage.getItem('riseai_login_time');
        if (loginTime) {
            const duration = Date.now() - parseInt(loginTime);
            const minutes = Math.floor(duration / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
        return '00:00';
    }
}

// Initialize authentication
const auth = new Auth();