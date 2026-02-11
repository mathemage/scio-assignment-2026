import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { GroupWithQR, Message, WebSocketMessage } from '../types';

const StudentGroupView: React.FC = () => {
  const { groupId } = useParams<{ groupId: string }>();
  const { token, user } = useAuth();
  const navigate = useNavigate();
  
  const [group, setGroup] = useState<GroupWithQR | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [myProgress, setMyProgress] = useState<number>(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!groupId || !token) return;
    
    loadGroupData();
    setupWebSocket();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [groupId, token]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadGroupData = async () => {
    if (!groupId || !token) return;
    
    try {
      const groupData = await apiService.getGroup(parseInt(groupId), token);
      setGroup(groupData);
      
      const messagesData = await apiService.getMessages(parseInt(groupId), token);
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load group data:', error);
    }
  };

  const setupWebSocket = () => {
    if (!groupId || !token) return;
    
    const websocket = apiService.createWebSocket(parseInt(groupId), token);
    
    websocket.onmessage = (event) => {
      const data: WebSocketMessage = JSON.parse(event.data);
      
      if (data.type === 'message') {
        setMessages(prev => [...prev, {
          id: data.id!,
          content: data.content!,
          user_id: data.user_id!,
          user_name: data.user_name!,
          group_id: parseInt(groupId),
          created_at: data.created_at!,
        }]);
      } else if (data.type === 'progress_update' && data.user_id === user?.id) {
        setMyProgress(data.progress!.progress_percentage);
      }
    };
    
    setWs(websocket);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newMessage.trim() || !ws) return;
    
    ws.send(JSON.stringify({
      type: 'message',
      content: newMessage.trim(),
    }));
    
    setNewMessage('');
  };

  if (!group) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button onClick={() => navigate('/dashboard')} style={styles.backButton}>
          ← Back to Dashboard
        </button>
        <div>
          <h1 style={styles.title}>{group.name}</h1>
          <p style={styles.goal}>Goal: {group.goal_description}</p>
        </div>
        <div style={styles.progressIndicator}>
          <span style={styles.progressLabel}>Your Progress:</span>
          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${myProgress}%`,
              }}
            />
          </div>
          <span style={styles.progressPercent}>{myProgress}%</span>
        </div>
      </div>

      <div style={styles.chatContainer}>
        <div style={styles.messagesArea}>
          {messages.length === 0 ? (
            <p style={styles.emptyMessage}>
              No messages yet. Start the conversation!
            </p>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  ...styles.message,
                  ...(msg.user_id === user?.id ? styles.myMessage : {}),
                }}
              >
                {msg.user_id !== user?.id && (
                  <div style={styles.messageName}>{msg.user_name}</div>
                )}
                <div style={styles.messageContent}>{msg.content}</div>
                <div style={styles.messageTime}>
                  {new Date(msg.created_at).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} style={styles.inputArea}>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            style={styles.input}
          />
          <button type="submit" style={styles.sendButton} disabled={!newMessage.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: 'white',
    padding: '20px 40px',
    borderBottom: '1px solid #e0e0e0',
  },
  backButton: {
    padding: '8px 16px',
    fontSize: '14px',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
    marginBottom: '16px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#333',
    margin: '0 0 8px 0',
  },
  goal: {
    fontSize: '14px',
    color: '#666',
    margin: '0 0 16px 0',
  },
  progressIndicator: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginTop: '16px',
  },
  progressLabel: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
  },
  progressBar: {
    flex: 1,
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4285F4',
    transition: 'width 0.3s',
  },
  progressPercent: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#4285F4',
    minWidth: '40px',
  },
  chatContainer: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    maxWidth: '1200px',
    width: '100%',
    margin: '0 auto',
    padding: '20px',
  },
  messagesArea: {
    flex: 1,
    overflowY: 'auto',
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    marginBottom: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  emptyMessage: {
    fontSize: '14px',
    color: '#999',
    textAlign: 'center',
    padding: '40px',
  },
  message: {
    maxWidth: '70%',
    padding: '12px 16px',
    borderRadius: '12px',
    backgroundColor: '#f0f0f0',
    alignSelf: 'flex-start',
  },
  myMessage: {
    backgroundColor: '#4285F4',
    color: 'white',
    alignSelf: 'flex-end',
  },
  messageName: {
    fontSize: '12px',
    fontWeight: '500',
    marginBottom: '4px',
    color: '#666',
  },
  messageContent: {
    fontSize: '14px',
    lineHeight: '1.5',
    marginBottom: '4px',
  },
  messageTime: {
    fontSize: '11px',
    opacity: 0.7,
  },
  inputArea: {
    display: 'flex',
    gap: '12px',
    backgroundColor: 'white',
    padding: '16px',
    borderRadius: '8px',
  },
  input: {
    flex: 1,
    padding: '12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontFamily: 'inherit',
  },
  sendButton: {
    padding: '12px 24px',
    fontSize: '14px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#4285F4',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    fontSize: '18px',
    color: '#666',
  },
};

export default StudentGroupView;
