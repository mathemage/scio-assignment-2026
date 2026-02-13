export interface User {
  id: number;
  email: string;
  name: string;
  role: 'teacher' | 'student';
  created_at: string;
}

export interface Group {
  id: number;
  name: string;
  goal_description: string;
  teacher_id: number;
  join_code: string;
  created_at: string;
}

export interface GroupWithQR extends Group {
  qr_code_url: string;
  join_url: string;
}

export interface Message {
  id: number;
  content: string;
  user_id: number;
  group_id: number;
  created_at: string;
  user_name: string;
}

export interface ProgressEstimate {
  user_id: number;
  user_name: string;
  progress_percentage: number;
  messages_count: number;
  last_message_time?: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

export interface WebSocketMessage {
  type: 'connected' | 'message' | 'progress_update';
  user_id?: number;
  user_name?: string;
  group_id?: number;
  id?: number;
  content?: string;
  created_at?: string;
  progress?: {
    progress_percentage: number;
    messages_count: number;
    last_message_time?: string;
  };
}
