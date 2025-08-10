import { fetchApi } from '../utils/api';

export type User = {
  email: string;
  full_name: string;
  role: 'employee' | 'manager';
};

export type LoginCredentials = {
  email: string;
  password: string;
};

export type RegisterData = {
  email: string;
  password: string;
  full_name: string;
  role: 'employee' | 'manager';
};

export const userService = {
  login: async (credentials: LoginCredentials) => {
    return fetchApi<{ success: boolean; message: string; user: User; token: string }>('/users/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },
  
  register: async (data: RegisterData) => {
    return fetchApi<{ success: boolean; message: string }>('/users/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  getCurrentUser: async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      return { success: false, error: 'No authentication token found' };
    }
    
    return fetchApi<{ user: User }>('/users/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};