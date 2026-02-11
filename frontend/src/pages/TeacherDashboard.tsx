import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { apiService } from '../services/api';
import { Group } from '../types';

const TeacherDashboard: React.FC = () => {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();
  const [groups, setGroups] = useState<Group[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newGroupName, setNewGroupName] = useState('');
  const [newGroupGoal, setNewGroupGoal] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadGroups();
  }, []);

  const loadGroups = async () => {
    if (!token) return;
    
    try {
      const data = await apiService.getGroups(token);
      setGroups(data);
    } catch (error) {
      console.error('Failed to load groups:', error);
    }
  };

  const handleCreateGroup = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    
    setIsLoading(true);
    try {
      await apiService.createGroup(newGroupName, newGroupGoal, token);
      setNewGroupName('');
      setNewGroupGoal('');
      setShowCreateForm(false);
      loadGroups();
    } catch (error) {
      console.error('Failed to create group:', error);
      alert('Failed to create group');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGroupClick = (groupId: number) => {
    navigate(`/teacher/group/${groupId}`);
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>Teacher Dashboard</h1>
          <p style={styles.subtitle}>Welcome, {user?.name}</p>
        </div>
        <button onClick={logout} style={styles.logoutButton}>
          Logout
        </button>
      </div>

      <div style={styles.content}>
        <div style={styles.buttonContainer}>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            style={styles.createButton}
          >
            {showCreateForm ? 'Cancel' : '+ Create New Group'}
          </button>
        </div>

        {showCreateForm && (
          <div style={styles.formCard}>
            <h2 style={styles.formTitle}>Create New Group</h2>
            <form onSubmit={handleCreateGroup} style={styles.form}>
              <div style={styles.formGroup}>
                <label style={styles.label}>Group Name</label>
                <input
                  type="text"
                  value={newGroupName}
                  onChange={(e) => setNewGroupName(e.target.value)}
                  placeholder="e.g., A2 – Quadratic equations 1"
                  style={styles.input}
                  required
                />
              </div>

              <div style={styles.formGroup}>
                <label style={styles.label}>Goal Description</label>
                <textarea
                  value={newGroupGoal}
                  onChange={(e) => setNewGroupGoal(e.target.value)}
                  placeholder="e.g., Solve independently 3 different quadratic equations ax^2 + bx + c using the discriminant"
                  style={{ ...styles.input, minHeight: '100px', resize: 'vertical' }}
                  required
                />
              </div>

              <button type="submit" style={styles.submitButton} disabled={isLoading}>
                {isLoading ? 'Creating...' : 'Create Group'}
              </button>
            </form>
          </div>
        )}

        <div style={styles.groupsSection}>
          <h2 style={styles.sectionTitle}>Your Groups</h2>
          
          {groups.length === 0 ? (
            <p style={styles.emptyMessage}>
              No groups yet. Create your first group to get started!
            </p>
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
                  <div style={styles.groupMeta}>
                    <span style={styles.metaText}>
                      Created: {new Date(group.created_at).toLocaleDateString()}
                    </span>
                  </div>
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
  buttonContainer: {
    marginBottom: '24px',
  },
  createButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#4285F4',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
  formCard: {
    backgroundColor: 'white',
    borderRadius: '8px',
    padding: '24px',
    marginBottom: '32px',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
  },
  formTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#333',
    marginBottom: '20px',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#333',
  },
  input: {
    padding: '12px',
    fontSize: '14px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontFamily: 'inherit',
  },
  submitButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '500',
    color: 'white',
    backgroundColor: '#4285F4',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    alignSelf: 'flex-start',
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
  emptyMessage: {
    fontSize: '14px',
    color: '#666',
    textAlign: 'center',
    padding: '40px',
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
    marginBottom: '12px',
  },
  groupMeta: {
    borderTop: '1px solid #e0e0e0',
    paddingTop: '12px',
  },
  metaText: {
    fontSize: '12px',
    color: '#999',
  },
};

export default TeacherDashboard;
