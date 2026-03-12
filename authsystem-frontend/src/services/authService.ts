import { api } from './axiosInstance';
import type { UserInfo } from '../contexts/AuthContext';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'https://localhost:7001';

export const authService = {
  /** Redirects the browser to the Google OAuth2 consent screen. */
  loginWithGoogle() {
    window.location.href = `${API_BASE}/auth/login/google`;
  },

  /** Calls POST /auth/logout — revokes refresh token and clears cookie. */
  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },

  /** Returns the current user from the JWT on the server. */
  async getMe(): Promise<UserInfo> {
    const { data } = await api.get<UserInfo>('/auth/me');
    return data;
  },
};
