import { createContext, useCallback, useContext, useState } from 'react';

export interface UserInfo {
  id: string;
  email: string;
  name: string;
  picture?: string;
}

interface AuthState {
  user: UserInfo | null;
  accessToken: string | null;
}

interface AuthContextValue extends AuthState {
  setTokens: (accessToken: string, user: UserInfo) => void;
  clearAuth: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, accessToken: null });

  const setTokens = useCallback((accessToken: string, user: UserInfo) => {
    setState({ user, accessToken });
  }, []);

  const clearAuth = useCallback(() => {
    setState({ user: null, accessToken: null });
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, setTokens, clearAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>');
  return ctx;
}
