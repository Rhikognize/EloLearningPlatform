import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { setAccessToken, clearAccessToken } from '../api/axios';
import { AuthContext } from './auth-context';
import api from '../api/axios';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const isInitialized = useRef(false);

  const restoreSession = useCallback(async () => {
    if (isInitialized.current) return;
    isInitialized.current = true;

    try {
      const { data: tokenData } = await api.post('/auth/refresh');
      setAccessToken(tokenData.access_token);

      const { data: userData } = await api.get('/users/me');
      setUser(userData);
    // eslint-disable-next-line no-unused-vars
    } catch (error) {
      clearAccessToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    restoreSession();
  }, [restoreSession]);

  const login = useCallback(async (data) => {
    setAccessToken(data.access_token);
    try {
      const { data: userData } = await api.get('/users/me');
      setUser(userData);
    } catch (error) {
      clearAccessToken();
      throw error;
    }
  }, []);

  const logout = useCallback(() => {
    clearAccessToken();
    setUser(null);
  }, []);

  const authValue = useMemo(() => ({
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user
  }), [user, loading, login, logout]);

  if (loading) {
    return (
      <div className="min-h-screen bg-base flex items-center justify-center">
        <div className="text-text-secondary text-sm">Se încarcă...</div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={authValue}>
      {children}
    </AuthContext.Provider>
  );
}