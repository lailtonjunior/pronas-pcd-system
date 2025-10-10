// Arquivo: frontend/src/contexts/AuthContext.tsx
"use client";

import { createContext, useState, useEffect, ReactNode, FC } from 'react';
import { apiClient } from '@/lib/api'; // Supondo que seu api client esteja em lib/api

// Defina uma interface para o usuário
interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'gestor' | 'auditor' | 'operador';
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  loading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('pronas_access_token');
    if (token) {
      apiClient.getCurrentUser()
        .then(userData => {
          setUser(userData);
        })
        .catch(() => {
          // Token inválido, limpa
          localStorage.removeItem('pronas_access_token');
          setUser(null);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = (token: string, userData: User) => {
    localStorage.setItem('pronas_access_token', token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('pronas_access_token');
    setUser(null);
    // Opcional: redirecionar para a página de login
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!user,
        user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};