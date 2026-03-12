import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { setAccessToken } from '../services/axiosInstance';
import type { UserInfo } from '../contexts/AuthContext';

interface AuthCallbackResponse {
  accessToken: string;
  expiresIn: number;
  user: UserInfo;
}

/**
 * The backend redirects here after a successful Google OAuth2 callback.
 * The API returns JSON with { accessToken, expiresIn, user }.
 * This page reads those values, stores the token in memory, and redirects.
 *
 * NOTE: Because the backend and frontend are on the same origin during dev
 * (proxied via Vite), the JSON response is received by the browser directly.
 * In production, configure Vite's proxy or CORS accordingly.
 */
export default function CallbackPage() {
  const navigate = useNavigate();
  const { setTokens, clearAuth } = useAuth();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    // The API server returns JSON on /auth/callback/google.
    // Vite proxies /auth/* → API, so we fetch the result ourselves.
    fetch('/auth/callback/google' + window.location.search, {
      credentials: 'include',
    })
      .then(res => {
        if (!res.ok) throw new Error('Authentication failed');
        return res.json() as Promise<AuthCallbackResponse>;
      })
      .then(data => {
        setAccessToken(data.accessToken);
        setTokens(data.accessToken, data.user);
        navigate('/', { replace: true });
      })
      .catch(() => {
        clearAuth();
        navigate('/login?error=auth_failed', { replace: true });
      });
  }, [navigate, setTokens, clearAuth]);

  return <p style={{ textAlign: 'center', marginTop: '10vh' }}>Completing sign-in…</p>;
}
