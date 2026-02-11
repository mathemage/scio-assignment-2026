import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { Group } from '../types';

const StudentDashboard: React.FC = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>([]);

  useEffect(() => {
    loadGroups();
  }, [token]);

  const loadGroups = async () => {
    if (!token) return;
    
    try {
      const data = await apiService.getGroups(token);
      setGroups(data);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const handleGroupClick = (groupId: number) => {
    navigate(`/student/group/${groupId}`);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Student Dashboard</h1>
          <p style={styles.subtitle}>Welcome, {user?.name}</p>
        </div>
        <button onClick={logout} style={styles.logoutButton}>
          Logout
        </button>
      </div>

      <div style={styles.content}>
        <div style={styles.groupsSection}>
          <h2 style={styles.sectionTitle}>Your Groups</h2>
          
          {groups.length === 0 ? (
            <div style={styles.emptyState}>
              <p style={styles.emptyMessage}>
                You haven't joined any groups yet.
              </p>
              <p style={styles.emptyHint}>
                Scan a QR code from your teacher to join a group!
              </p>
            </div>
          ) : (
            <div style={styles.groupsGrid}>
              {groups.map((group) => (
                <div
                  key={group.id}
                  style={styles.groupCard}
                  onClick={() => handleGroupClick(group.id)}
                >
                  <h3 style={styles.groupName}>{group.name}</h3>
                  <p style={styles.groupGoal}>{group.goal_description}</p>
                </div>
              ))}
            </div>
          )}
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
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#333',
    margin: 0,
  },
  subtitle: {
    fontSize: '14px',
    color: '#666',
    margin: '4px 0 0 0',
  },
  logoutButton: {
    padding: '8px 16px',
    fontSize: '14px',
    color: '#666',
    backgroundColor: 'white',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  content: {
    padding: '40px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  groupsSection: {
    marginTop: '32px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '16px',
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
  },
  emptyMessage: {
    fontSize: '16px',
    color: '#666',
    marginBottom: '8px',
  },
  emptyHint: {
    fontSize: '14px',
    color: '#999',
  },
  groupsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
    gap: '20px',
  },
  groupCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
  },
  groupName: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '8px',
  },
  groupGoal: {
    fontSize: '14px',
    color: '#666',
    lineHeight: '1.5',
  },
};

export default StudentDashboard;
