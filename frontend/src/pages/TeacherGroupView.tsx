import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { GroupWithQR, ProgressEstimate, Message, WebSocketMessage } from '../types';
import QRCode from 'react-qr-code';

const TeacherGroupView: React.FC = () => {
  const { groupId } = useParams<{ groupId: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  
  const [group, setGroup] = useState<GroupWithQR | null>(null);
  const [progress, setProgress] = useState<ProgressEstimate[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!groupId || !token) return;
    
    loadGroupData();
    setupWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [groupId, token]);

  const loadGroupData = async () => {
    if (!groupId || !token) return;
    
    try {
      const groupData = await apiService.getGroup(parseInt(groupId), token);
      setGroup(groupData);
      
      const progressData = await apiService.getProgress(parseInt(groupId), token);
      setProgress(progressData);
      
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
      } else if (data.type === 'progress_update') {
        setProgress(prev => {
          const updated = prev.filter(p => p.user_id !== data.user_id);
          return [...updated, {
            user_id: data.user_id!,
            user_name: data.user_name!,
            progress_percentage: data.progress!.progress_percentage,
            messages_count: data.progress!.messages_count,
            last_message_time: data.progress!.last_message_time,
          }];
        });
      }
    };
    
    wsRef.current = websocket;
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
        <h1 style={styles.title}>{group.name}</h1>
        <p style={styles.goal}>Goal: {group.goal_description}</p>
      </div>

      <div style={styles.content}>
        <div style={styles.leftColumn}>
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Join QR Code</h2>
            <div style={styles.qrContainer}>
              <QRCode value={group.join_url} size={200} />
            </div>
            <p style={styles.joinUrl}>
              Join URL: <a href={group.join_url} target="_blank" rel="noopener noreferrer">
                {group.join_url}
              </a>
            </p>
          </div>

          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Student Progress</h2>
            {progress.length === 0 ? (
              <p style={styles.emptyMessage}>No students have joined yet.</p>
            ) : (
              <div style={styles.progressList}>
                {progress.map((p) => (
                  <div key={p.user_id} style={styles.progressItem}>
                    <div style={styles.progressHeader}>
                      <span style={styles.studentName}>{p.user_name}</span>
                      <span style={styles.progressPercent}>{p.progress_percentage}%</span>
                    </div>
                    <div style={styles.progressBar}>
                      <div
                        style={{
                          ...styles.progressFill,
                          width: `${p.progress_percentage}%`,
                        }}
                      />
                    </div>
                    <div style={styles.progressMeta}>
                      <span>Messages: {p.messages_count}</span>
                      {p.last_message_time && (
                        <span>Last active: {new Date(p.last_message_time).toLocaleTimeString()}</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div style={styles.rightColumn}>
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Live Chat</h2>
            <div style={styles.messageContainer}>
              {messages.length === 0 ? (
                <p style={styles.emptyMessage}>No messages yet.</p>
              ) : (
                messages.map((msg) => (
                  <div key={msg.id} style={styles.message}>
                    <div style={styles.messageHeader}>
                      <span style={styles.messageName}>{msg.user_name}</span>
                      <span style={styles.messageTime}>
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <p style={styles.messageContent}>{msg.content}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
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
    margin: 0,
  },
  content: {
    padding: '40px',
    display: 'grid',
    gridTemplateColumns: '400px 1fr',
    gap: '24px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  leftColumn: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  rightColumn: {
    display: 'flex',
    flexDirection: 'column',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '16px',
  },
  qrContainer: {
    display: 'flex',
    justifyContent: 'center',
    padding: '20px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
    marginBottom: '16px',
  },
  joinUrl: {
    fontSize: '12px',
    color: '#666',
    wordBreak: 'break-all',
  },
  emptyMessage: {
    fontSize: '14px',
    color: '#999',
    textAlign: 'center',
    padding: '20px',
  },
  progressList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  progressItem: {
    padding: '12px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
  },
  progressHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '8px',
  },
  studentName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
  },
  progressPercent: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#4285F4',
  },
  progressBar: {
    height: '8px',
    backgroundColor: '#e0e0e0',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '8px',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#4285F4',
    transition: 'width 0.3s',
  },
  progressMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
    color: '#999',
  },
  messageContainer: {
    maxHeight: '600px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  message: {
    padding: '12px',
    backgroundColor: '#f9f9f9',
    borderRadius: '8px',
  },
  messageHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '4px',
  },
  messageName: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
  },
  messageTime: {
    fontSize: '12px',
    color: '#999',
  },
  messageContent: {
    fontSize: '14px',
    color: '#666',
    margin: 0,
    lineHeight: '1.5',
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

export default TeacherGroupView;
