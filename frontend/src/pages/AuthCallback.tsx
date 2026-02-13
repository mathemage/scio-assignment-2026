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
      
      if (token) {
        const success = await login(token);
        if (success) {
          navigate('/dashboard');
        } else {
          navigate('/login');
        }
      } else {
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
