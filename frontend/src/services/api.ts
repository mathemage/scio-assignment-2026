import { User, Group, GroupWithQR, Message, ProgressEstimate } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private getHeaders(token?: string): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Use provided token or fall back to stored token
    let authToken = token;
    if (!authToken) {
      try {
        authToken = localStorage.getItem('auth_token') || undefined;
      } catch (e) {
        // localStorage may be unavailable (e.g., incognito mode with strict settings)
        console.warn('localStorage access failed:', e);
      }
    }
    
    if (authToken) {
      headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    return headers;
  }

  private async request<T>(url: string, options: RequestInit = {}, token?: string): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(token),
        ...options.headers,
      },
      credentials: 'include',
    });
    
    if (!response.ok) {
      // Try to extract error detail from response body
      try {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Request failed: ${response.statusText}`);
      } catch (parseError) {
        // If response is not JSON or already consumed, use status text
        throw new Error(`Request failed: ${response.statusText}`);
      }
    }
    
    return response.json();
  }

  // Authentication
  async getCurrentUser(token: string): Promise<User> {
    return this.request<User>(`${API_BASE_URL}/auth/me`, {}, token);
  }

  async setUserRole(userId: number, role: 'teacher' | 'student', token: string): Promise<any> {
    return this.request<any>(
      `${API_BASE_URL}/auth/set-role/${userId}?role=${role}`,
      { method: 'POST' },
      token
    );
  }

  // Groups
  async createGroup(name: string, goalDescription: string, token: string): Promise<GroupWithQR> {
    return this.request<GroupWithQR>(
      `${API_BASE_URL}/groups/`,
      {
        method: 'POST',
        body: JSON.stringify({
          name,
          goal_description: goalDescription,
        }),
      },
      token
    );
  }

  async getGroups(token: string): Promise<Group[]> {
    return this.request<Group[]>(`${API_BASE_URL}/groups/`, {}, token);
  }

  async getGroup(groupId: number, token: string): Promise<GroupWithQR> {
    return this.request<GroupWithQR>(`${API_BASE_URL}/groups/${groupId}`, {}, token);
  }

  async joinGroup(joinCode: string, deviceId: string | null, token: string): Promise<any> {
    return this.request<any>(
      `${API_BASE_URL}/groups/join`,
      {
        method: 'POST',
        body: JSON.stringify({
          join_code: joinCode,
          device_id: deviceId,
        }),
      },
      token
    );
  }

  async getGroupMembers(groupId: number, token: string): Promise<any> {
    return this.request<any>(`${API_BASE_URL}/groups/${groupId}/members`, {}, token);
  }

  // Chat
  async getMessages(groupId: number, token: string): Promise<Message[]> {
    return this.request<Message[]>(`${API_BASE_URL}/chat/${groupId}/messages`, {}, token);
  }

  async getProgress(groupId: number, token: string): Promise<ProgressEstimate[]> {
    return this.request<ProgressEstimate[]>(`${API_BASE_URL}/chat/${groupId}/progress`, {}, token);
  }

  // WebSocket
  createWebSocket(groupId: number, token: string): WebSocket {
    const wsUrl = API_BASE_URL.replace('http', 'ws');
    // Note: In production, consider using WebSocket subprotocols or sending token
    // in the first message after connection to avoid exposing it in URL/logs
    return new WebSocket(`${wsUrl}/chat/ws/${groupId}?token=${token}`);
  }
}

export const apiService = new ApiService();
