import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/authService';
import { setAccessToken } from '../services/axiosInstance';
import { useNavigate } from 'react-router-dom';

export default function DashboardPage() {
  const { user, clearAuth } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await authService.logout();
    setAccessToken(null);
    clearAuth();
    navigate('/login', { replace: true });
  };

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Dashboard</h1>
      {user && (
        <>
          <p>Welcome, <strong>{user.name}</strong> ({user.email})</p>
          {user.picture && <img src={user.picture} alt="avatar" width={48} height={48} referrerPolicy="no-referrer" />}
        </>
      )}
      <button onClick={handleLogout} style={{ marginTop: '1rem', padding: '0.5rem 1.5rem', cursor: 'pointer' }}>
        Sign out
      </button>
    </div>
  );
}
