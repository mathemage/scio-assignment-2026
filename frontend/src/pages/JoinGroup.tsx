import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { getDeviceId, hasJoinedGroup, markGroupJoined } from '../utils/device';

const JoinGroup: React.FC = () => {
  const { joinCode } = useParams<{ joinCode: string }>();
  const { token, user } = useAuth();
  const navigate = useNavigate();
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      // Not logged in, redirect to login
      navigate('/login');
      return;
    }

    if (joinCode) {
      handleJoin();
    }
  }, [joinCode, token]);

  const handleJoin = async () => {
    if (!joinCode || !token) return;

    setIsJoining(true);
    setError(null);

    try {
      const deviceId = getDeviceId();
      
      // Join the group
      const result = await apiService.joinGroup(joinCode, deviceId, token);
      
      // Mark as joined in localStorage
      markGroupJoined(result.group_id);
      
      // Redirect to the group
      if (user?.role === 'student') {
        navigate(`/student/group/${result.group_id}`);
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      console.error('Failed to join group:', err);
      setError(err.message || 'Failed to join group');
      setIsJoining(false);
    }
  };

  if (isJoining) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Joining group...</h2>
          <p style={styles.message}>Please wait</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Error</h2>
          <p style={styles.error}>{error}</p>
          <button onClick={() => navigate('/dashboard')} style={styles.button}>
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Processing...</h2>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '40px',
    boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
    maxWidth: '400px',
    width: '100%',
    textAlign: 'center',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '16px',
  },
  message: {
    fontSize: '14px',
    color: '#666',
  },
  error: {
    fontSize: '14px',
    color: '#d32f2f',
    marginBottom: '20px',
  },
  button: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#4285F4',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default JoinGroup;
