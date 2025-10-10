// Arquivo: frontend/src/lib/api.ts

import { LoginRequest, LoginResponse, User, Project, Institution } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    if (typeof window !== 'undefined') {
      this.setToken(localStorage.getItem('pronas_access_token'));
    }
  }

  public setToken(token: string | null) {
    this.token = token;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const config: RequestInit = {
      ...options,
      headers: this.getHeaders(),
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }
    // Handle responses with no content
    if (response.status === 204) {
        return null as T;
    }
    return response.json();
  }

  // === AUTHENTICATION ===
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Corrigido para enviar JSON com 'email'
    const response = await this.request<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (response.access_token) {
      this.setToken(response.access_token);
      if (typeof window !== 'undefined') {
        localStorage.setItem('pronas_access_token', response.access_token);
      }
    }
    return response;
  }

  async logout(): Promise<void> {
    // Implementação de logout, se houver um endpoint no backend
    this.setToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('pronas_access_token');
    }
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // === INSTITUTIONS ===
  async getInstitutions(): Promise<{ items: Institution[] }> {
    return this.request<{ items: Institution[] }>('/institutions/');
  }

  async createInstitution(data: any): Promise<Institution> {
    return this.request<Institution>('/institutions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // === PROJECTS ===
  async getProjects(): Promise<{ items: Project[] }> {
    return this.request<{ items: Project[] }>('/projects/');
  }
}

export const apiClient = new ApiClient(API_BASE_URL);