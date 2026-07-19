'use client';
/* ============================================================
   CrimeLens AI — Auth Context & Provider
   Manages authentication state, token storage, and protected routes.
   ============================================================ */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';
import { authAPI } from './api';
import type { User } from './types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  loginWithGoogle: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'crimelens_token';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /** Load user profile from stored token on mount */
  useEffect(() => {
    const token = Cookies.get(TOKEN_KEY);
    if (token) {
      authAPI.getProfile()
        .then((res: any) => setUser(res.data))
        .catch(() => {
          Cookies.remove(TOKEN_KEY);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const res: any = await authAPI.login({ email, password });
    const { access_token, user: userData } = res.data;
    Cookies.set(TOKEN_KEY, access_token, { expires: 1, sameSite: 'strict' });
    setUser(userData);
  }, []);

  const register = useCallback(async (email: string, password: string, fullName: string) => {
    const res: any = await authAPI.register({ email, password, full_name: fullName });
    const { access_token, user: userData } = res.data;
    Cookies.set(TOKEN_KEY, access_token, { expires: 1, sameSite: 'strict' });
    setUser(userData);
  }, []);

  const loginWithGoogle = useCallback(async (token: string) => {
    const res: any = await authAPI.googleLogin(token);
    const { access_token, user: userData } = res.data;
    Cookies.set(TOKEN_KEY, access_token, { expires: 1, sameSite: 'strict' });
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    Cookies.remove(TOKEN_KEY);
    setUser(null);
    window.location.href = '/login';
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
