import { authService } from '../services/authService';

export default function LoginPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginTop: '10vh', gap: '1.5rem' }}>
      <h1>AuthSystem</h1>
      <p>Sign in to continue</p>
      <button
        onClick={() => authService.loginWithGoogle()}
        style={{ padding: '0.75rem 2rem', fontSize: '1rem', cursor: 'pointer' }}
      >
        Sign in with Google
      </button>
    </div>
  );
}
