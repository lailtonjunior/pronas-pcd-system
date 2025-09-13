#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 3 - PARTE 2
# PRONAS/PCD System - Auth System + API Client
# Execute após aplicar a Parte 1

set -e

echo "🚀 LOTE 3 PARTE 2: Sistema de Autenticação e API Client"
echo "======================================================"

if [ ! -d "frontend/src" ]; then
    echo "❌ Execute a Parte 1 primeiro."
    exit 1
fi

cd frontend

echo "📝 Criando sistema de autenticação..."

# Types
mkdir -p src/lib/types
cat > src/lib/types/auth.ts << 'EOF'
export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'gestor' | 'auditor' | 'operador';
  status: 'active' | 'inactive' | 'pending' | 'suspended';
  is_active: boolean;
  institution_id?: number;
  last_login?: string;
  consent_given: boolean;
  consent_date?: string;
  created_at: string;
  updated_at?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
EOF

# API Types
cat > src/lib/types/api.ts << 'EOF'
export interface ApiError {
  detail: string;
  status?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
  has_more: boolean;
}

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  status: 'success' | 'error';
}
EOF

# Token utilities
mkdir -p src/lib/auth
cat > src/lib/auth/tokens.ts << 'EOF'
import Cookies from 'js-cookie';

const ACCESS_TOKEN_KEY = 'pronas_access_token';
const REFRESH_TOKEN_KEY = 'pronas_refresh_token';

export function getToken(): string | undefined {
  return Cookies.get(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | undefined {
  return Cookies.get(REFRESH_TOKEN_KEY);
}

export function setTokens(accessToken: string, refreshToken: string): void {
  // Set tokens with secure options
  const options = {
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict' as const,
    expires: 7, // 7 days
  };

  Cookies.set(ACCESS_TOKEN_KEY, accessToken, options);
  Cookies.set(REFRESH_TOKEN_KEY, refreshToken, {
    ...options,
    expires: 30, // 30 days for refresh token
  });
}

export function removeTokens(): void {
  Cookies.remove(ACCESS_TOKEN_KEY);
  Cookies.remove(REFRESH_TOKEN_KEY);
}

export function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}
EOF

# API Client
mkdir -p src/lib/api
cat > src/lib/api/client.ts << 'EOF'
import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { getToken, getRefreshToken, setTokens, removeTokens, isTokenExpired } from '@/lib/auth/tokens';
import toast from 'react-hot-toast';

class ApiClient {
  private instance: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.instance = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.instance.interceptors.request.use(
      async (config) => {
        const token = getToken();
        
        if (token && !isTokenExpired(token)) {
          config.headers.Authorization = `Bearer ${token}`;
        } else if (token && isTokenExpired(token)) {
          // Try to refresh token
          try {
            const newToken = await this.refreshAccessToken();
            config.headers.Authorization = `Bearer ${newToken}`;
          } catch (error) {
            // Refresh failed, redirect to login
            this.handleAuthError();
            return Promise.reject(error);
          }
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.instance(originalRequest);
          } catch (refreshError) {
            this.handleAuthError();
            return Promise.reject(refreshError);
          }
        }

        // Handle other errors
        this.handleError(error);
        return Promise.reject(error);
      }
    );
  }

  private async refreshAccessToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = this.performTokenRefresh();

    try {
      const newToken = await this.refreshPromise;
      return newToken;
    } finally {
      this.refreshPromise = null;
    }
  }

  private async performTokenRefresh(): Promise<string> {
    const refreshToken = getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken }
    );

    const { access_token, refresh_token } = response.data;
    setTokens(access_token, refresh_token);
    
    return access_token;
  }

  private handleAuthError() {
    removeTokens();
    
    // Redirect to login if not already there
    if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
      window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
    }
  }

  private handleError(error: AxiosError) {
    if (error.response?.status === 400) {
      const message = (error.response.data as any)?.detail || 'Requisição inválida';
      toast.error(message);
    } else if (error.response?.status === 403) {
      toast.error('Você não tem permissão para realizar esta ação');
    } else if (error.response?.status === 404) {
      toast.error('Recurso não encontrado');
    } else if (error.response?.status >= 500) {
      toast.error('Erro interno do servidor. Tente novamente mais tarde.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Tempo limite da requisição excedido');
    } else if (!error.response) {
      toast.error('Erro de conexão. Verifique sua internet.');
    }
  }

  // HTTP Methods
  async get<T = any>(url: string, params?: any): Promise<T> {
    const response = await this.instance.get(url, { params });
    return response.data;
  }

  async post<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.post(url, data);
    return response.data;
  }

  async put<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.put(url, data);
    return response.data;
  }

  async delete<T = any>(url: string): Promise<T> {
    const response = await this.instance.delete(url);
    return response.data;
  }

  async patch<T = any>(url: string, data?: any): Promise<T> {
    const response = await this.instance.patch(url, data);
    return response.data;
  }
}

export const apiClient = new ApiClient();
EOF

# Auth API functions
cat > src/lib/api/auth.ts << 'EOF'
import { apiClient } from './client';
import { LoginRequest, LoginResponse, User } from '@/lib/types/auth';

export const authApi = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return apiClient.post('/api/v1/auth/login', credentials);
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/v1/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get('/api/v1/auth/me');
  },

  async changePassword(data: {
    old_password: string;
    new_password: string;
  }): Promise<void> {
    return apiClient.post('/api/v1/auth/change-password', data);
  },
};
EOF

# Auth Context
cat > src/lib/auth/auth-context.tsx << 'EOF'
'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { User, AuthState, LoginRequest } from '@/lib/types/auth';
import { authApi } from '@/lib/api/auth';
import { getToken, setTokens, removeTokens } from './tokens';
import toast from 'react-hot-toast';

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const router = useRouter();

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    const token = getToken();
    
    if (!token) {
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
      return;
    }

    try {
      const user = await authApi.getCurrentUser();
      setAuthState({
        user,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      // Token is invalid
      removeTokens();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  };

  const login = async (credentials: LoginRequest) => {
    try {
      const response = await authApi.login(credentials);
      
      // Store tokens
      setTokens(response.access_token, response.refresh_token);
      
      // Update state
      setAuthState({
        user: response.user,
        isAuthenticated: true,
        isLoading: false,
      });

      toast.success('Login realizado com sucesso!');
      
      // Redirect to dashboard or intended page
      const redirectUrl = new URLSearchParams(window.location.search).get('redirect') || '/dashboard';
      router.push(redirectUrl);
      
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Erro ao fazer login';
      toast.error(message);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Erro ao fazer logout:', error);
    } finally {
      removeTokens();
      setAuthState({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
      
      toast.success('Logout realizado com sucesso!');
      router.push('/login');
    }
  };

  const refreshUser = async () => {
    try {
      const user = await authApi.getCurrentUser();
      setAuthState(prev => ({
        ...prev,
        user,
      }));
    } catch (error) {
      console.error('Erro ao atualizar dados do usuário:', error);
    }
  };

  const value: AuthContextType = {
    ...authState,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
EOF

echo "✅ Sistema de autenticação criado!"

echo "📝 Criando utilitários e hooks..."

# Utilities
mkdir -p src/lib/utils
cat > src/lib/utils/format.ts << 'EOF'
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export function formatDate(date: string | Date, pattern: string = 'dd/MM/yyyy'): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return format(dateObj, pattern, { locale: ptBR });
}

export function formatDateTime(date: string | Date): string {
  return formatDate(date, 'dd/MM/yyyy HH:mm');
}

export function formatRelativeTime(date: string | Date): string {
  const dateObj = typeof date === 'string' ? parseISO(date) : date;
  return formatDistanceToNow(dateObj, { addSuffix: true, locale: ptBR });
}

export function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  }).format(value);
}

export function formatCPF(cpf: string): string {
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

export function formatCNPJ(cnpj: string): string {
  return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
}
EOF

# Validation utilities
cat > src/lib/utils/validation.ts << 'EOF'
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isValidCPF(cpf: string): boolean {
  // Remove non-digits
  const cleanCPF = cpf.replace(/\D/g, '');
  
  if (cleanCPF.length !== 11) return false;
  
  // Check for repeated digits
  if (/^(\d)\1{10}$/.test(cleanCPF)) return false;
  
  // Validate check digits
  let sum = 0;
  for (let i = 0; i < 9; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (10 - i);
  }
  
  let digit1 = ((sum * 10) % 11) % 10;
  if (digit1 !== parseInt(cleanCPF.charAt(9))) return false;
  
  sum = 0;
  for (let i = 0; i < 10; i++) {
    sum += parseInt(cleanCPF.charAt(i)) * (11 - i);
  }
  
  let digit2 = ((sum * 10) % 11) % 10;
  return digit2 === parseInt(cleanCPF.charAt(10));
}

export function isValidCNPJ(cnpj: string): boolean {
  const cleanCNPJ = cnpj.replace(/\D/g, '');
  
  if (cleanCNPJ.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cleanCNPJ)) return false;
  
  // Validation algorithm
  const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  
  let sum = 0;
  for (let i = 0; i < 12; i++) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weights1[i];
  }
  
  let digit1 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  if (digit1 !== parseInt(cleanCNPJ.charAt(12))) return false;
  
  sum = 0;
  for (let i = 0; i < 13; i++) {
    sum += parseInt(cleanCNPJ.charAt(i)) * weights2[i];
  }
  
  let digit2 = sum % 11 < 2 ? 0 : 11 - (sum % 11);
  return digit2 === parseInt(cleanCNPJ.charAt(13));
}
EOF

# Common utilities
cat > src/lib/utils/index.ts << 'EOF'
import { clsx, type ClassValue } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function debounce<T extends (...args: any[]) => void>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

export * from './format';
export * from './validation';
EOF

# Custom hooks
mkdir -p src/lib/hooks
cat > src/lib/hooks/useLocalStorage.ts << 'EOF'
import { useState, useEffect } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  // State to store our value
  const [storedValue, setStoredValue] = useState<T>(initialValue);

  useEffect(() => {
    try {
      // Get from local storage by key
      const item = window.localStorage.getItem(key);
      // Parse stored json or if none return initialValue
      if (item) {
        setStoredValue(JSON.parse(item));
      }
    } catch (error) {
      // If error also return initialValue
      console.error(`Error reading localStorage key "${key}":`, error);
      setStoredValue(initialValue);
    }
  }, [key, initialValue]);

  // Return a wrapped version of useState's setter function that ...
  // ... persists the new value to localStorage.
  const setValue = (value: T) => {
    try {
      // Allow value to be a function so we have the same API as useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      // Save state
      setStoredValue(valueToStore);
      // Save to local storage
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      // A more advanced implementation would handle the error case
      console.error(`Error setting localStorage key "${key}":`, error);
    }
  };

  return [storedValue, setValue];
}
EOF

echo "✅ Utilitários criados!"

cd ..

echo ""
echo "🎉 LOTE 3 PARTE 2 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Sistema de autenticação completo com Context API"
echo "• Cliente API com interceptadores e refresh automático"
echo "• Gerenciamento de tokens JWT com cookies seguros"
echo "• Utilitários para formatação, validação e hooks"
echo "• Types TypeScript para Auth e API"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 3 Parte 3 (UI Components)"
echo "2. Execute: cd frontend && npm install"
echo ""
echo "📊 Status:"
echo "• Lote 3.1: ✅ Frontend base"
echo "• Lote 3.2: ✅ Auth + API Client"
echo "• Lote 3.3: ⏳ UI Components (próximo)"
echo ""