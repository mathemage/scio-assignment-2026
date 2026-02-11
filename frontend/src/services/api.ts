import { User, Group, GroupWithQR, Message, ProgressEstimate } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  private getHeaders(token?: string): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    return headers;
  }

  // Authentication
  async getCurrentUser(token: string): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get current user');
    }
    
    return response.json();
  }

  async setUserRole(userId: number, role: 'teacher' | 'student', token: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/auth/set-role/${userId}?role=${role}`, {
      method: 'POST',
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to set user role');
    }
    
    return response.json();
  }

  // Groups
  async createGroup(name: string, goalDescription: string, token: string): Promise<GroupWithQR> {
    const response = await fetch(`${API_BASE_URL}/groups/`, {
      method: 'POST',
      headers: this.getHeaders(token),
      body: JSON.stringify({
        name,
        goal_description: goalDescription,
      }),
    });
    
    if (!response.ok) {
      throw new Error('Failed to create group');
    }
    
    return response.json();
  }

  async getGroups(token: string): Promise<Group[]> {
    const response = await fetch(`${API_BASE_URL}/groups/`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get groups');
    }
    
    return response.json();
  }

  async getGroup(groupId: number, token: string): Promise<GroupWithQR> {
    const response = await fetch(`${API_BASE_URL}/groups/${groupId}`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get group');
    }
    
    return response.json();
  }

  async joinGroup(joinCode: string, deviceId: string | null, token: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/groups/join`, {
      method: 'POST',
      headers: this.getHeaders(token),
      body: JSON.stringify({
        join_code: joinCode,
        device_id: deviceId,
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to join group');
    }
    
    return response.json();
  }

  async getGroupMembers(groupId: number, token: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/groups/${groupId}/members`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get group members');
    }
    
    return response.json();
  }

  // Chat
  async getMessages(groupId: number, token: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE_URL}/chat/${groupId}/messages`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get messages');
    }
    
    return response.json();
  }

  async getProgress(groupId: number, token: string): Promise<ProgressEstimate[]> {
    const response = await fetch(`${API_BASE_URL}/chat/${groupId}/progress`, {
      headers: this.getHeaders(token),
    });
    
    if (!response.ok) {
      throw new Error('Failed to get progress');
    }
    
    return response.json();
  }

  // WebSocket
  createWebSocket(groupId: number, token: string): WebSocket {
    const wsUrl = API_BASE_URL.replace('http', 'ws');
    return new WebSocket(`${wsUrl}/chat/ws/${groupId}?token=${token}`);
  }
}

export const apiService = new ApiService();
