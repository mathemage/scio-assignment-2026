import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const AuthCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const handleAuth = async () => {
      const token = searchParams.get('token');
      console.log('[AuthCallback] Token from URL:', token ? token.substring(0, 20) + '...' : 'null');
      
      if (token) {
        console.log('[AuthCallback] Calling login with token...');
        const success = await login(token);
        console.log('[AuthCallback] Login result:', success);
        if (success) {
          console.log('[AuthCallback] Navigating to /dashboard');
          navigate('/dashboard');
        } else {
          console.log('[AuthCallback] Login failed, navigating to /login');
          navigate('/login');
        }
      } else {
        console.log('[AuthCallback] No token found, navigating to /login');
        navigate('/login');
      }
    };
    
    handleAuth();
  }, [searchParams, login, navigate]);

  return (
    <div style={styles.container}>
      <p>Authenticating...</p>
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
  },
};

export default AuthCallback;
