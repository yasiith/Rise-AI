import { fetchApi } from '../utils/api';

export type ChatMessage = {
  username: string;
  user_message: string;
  ai_response: string;
  timestamp: string;
};

export type ChatResponse = {
  success: boolean;
  response: string;
  timestamp: string;
};

export const chatService = {
  sendMessage: async (username: string, message: string) => {
    return fetchApi<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify({
        username,
        message,
        timestamp: new Date().toISOString(),
      }),
    });
  },
  
  getChatHistory: async (username: string, limit: number = 10) => {
    return fetchApi<{ success: boolean, history: ChatMessage[] }>(`/chat/history/${username}?limit=${limit}`);
  },
  
  clearChatHistory: async (username: string) => {
    return fetchApi<{ success: boolean, message: string }>(`/chat/history/${username}`, {
      method: 'DELETE',
    });
  },
  
  checkChatStatus: async () => {
    return fetchApi<{ success: boolean, status: string, ai_simulation: boolean }>('/chat/status');
  }
};