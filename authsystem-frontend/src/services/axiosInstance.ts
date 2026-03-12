import axios, { AxiosError } from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'https://localhost:7001';

// Module-level reference so the interceptor can always get the latest token.
// This is set by AuthContext via setAccessToken().
let _accessToken: string | null = null;
let _onUnauthenticated: (() => void) | null = null;

export function setAccessToken(token: string | null) {
  _accessToken = token;
}

export function setUnauthenticatedHandler(handler: () => void) {
  _onUnauthenticated = handler;
}

export const api = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // send HttpOnly refresh-token cookie on same-site requests
});

// Queue of requests waiting while a token refresh is in flight
let isRefreshing = false;
let waitQueue: Array<(token: string) => void> = [];

function drainQueue(newToken: string) {
  waitQueue.forEach(resolve => resolve(newToken));
  waitQueue = [];
}

// ── Request interceptor — attach Bearer token ─────────────────────────────────
api.interceptors.request.use(config => {
  if (_accessToken) {
    config.headers.Authorization = `Bearer ${_accessToken}`;
  }
  return config;
});

// ── Response interceptor — silent token refresh on 401 ───────────────────────
api.interceptors.response.use(
  response => response,
  async (error: AxiosError) => {
    const original = error.config as (typeof error.config & { _retry?: boolean });

    if (error.response?.status !== 401 || original?._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Queue this request until the ongoing refresh completes
      return new Promise(resolve => {
        waitQueue.push((token: string) => {
          original!.headers!.Authorization = `Bearer ${token}`;
          resolve(api(original!));
        });
      });
    }

    original._retry = true;
    isRefreshing = true;

    try {
      const { data } = await api.post<{ accessToken: string }>('/auth/refresh');
      setAccessToken(data.accessToken);
      original!.headers!.Authorization = `Bearer ${data.accessToken}`;
      drainQueue(data.accessToken);
      return api(original!);
    } catch {
      waitQueue = [];
      _onUnauthenticated?.();
      return Promise.reject(error);
    } finally {
      isRefreshing = false;
    }
  }
);
