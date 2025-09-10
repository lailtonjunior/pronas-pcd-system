/**
 * Cliente API para comunicação com o backend PRONAS/PCD
 */

import { LoginRequest, LoginResponse, ApiResponse, ApiError } from '@/types/pronas';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    // Recuperar token do localStorage se disponível
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('pronas_access_token');
    }
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

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Autenticação
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${this.baseURL}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();

    if (response.ok && data.access_token) {
      this.token = data.access_token;
      if (typeof window !== 'undefined') {
        localStorage.setItem('pronas_access_token', data.access_token);
      }
    }

    return data;
  }

  async logout(): Promise<void> {
    try {
      await this.request('/auth/logout', { method: 'POST' });
    } finally {
      this.token = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('pronas_access_token');
      }
    }
  }

  async getCurrentUser(): Promise<any> {
    return this.request('/auth/me');
  }

  // Instituições
  async getInstitutions(params?: {
    skip?: number;
    limit?: number;
    credential_status?: string;
    institution_type?: string;
    search?: string;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    return this.request(`/institutions/${query ? `?${query}` : ''}`);
  }

  async getInstitution(id: number): Promise<any> {
    return this.request(`/institutions/${id}`);
  }

  async createInstitution(data: any): Promise<any> {
    return this.request('/institutions/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateInstitution(id: number, data: any): Promise<any> {
    return this.request(`/institutions/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async requestCredential(id: number, documents: File[]): Promise<any> {
    const formData = new FormData();
    documents.forEach(file => {
      formData.append('documents', file);
    });

    return fetch(`${this.baseURL}/institutions/${id}/credential`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    }).then(res => res.json());
  }

  // Projetos
  async getProjects(params?: {
    skip?: number;
    limit?: number;
    status_filter?: string;
    institution_id?: number;
    field_of_action?: string;
    priority_area_id?: number;
    search?: string;
  }): Promise<any> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }
    
    const query = searchParams.toString();
    return this.request(`/projects/${query ? `?${query}` : ''}`);
  }

  async getProject(id: number): Promise<any> {
    return this.request(`/projects/${id}`);
  }

  async createProject(data: any): Promise<any> {
    return this.request('/projects/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateProject(id: number, data: any): Promise<any> {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async validateProject(id: number): Promise<any> {
    return this.request(`/projects/${id}/validate`, {
      method: 'POST',
    });
  }

  async submitProject(id: number): Promise<any> {
    return this.request(`/projects/${id}/submit`, {
      method: 'PUT',
    });
  }

  // IA
  async generateProject(data: any): Promise<any> {
    return this.request('/ai/generate-project', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getPriorityAreas(): Promise<any> {
    return this.request('/ai/priority-areas');
  }

  // Monitoramento
  async getProjectMonitoring(id: number): Promise<any> {
    return this.request(`/projects/${id}/monitoring`);
  }

  async addMonitoringEntry(id: number, data: any): Promise<any> {
    return this.request(`/projects/${id}/monitoring`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Dashboard
  async getDashboardData(): Promise<any> {
    return this.request('/reports/dashboard');
  }

  // Sistema
  async getSystemConfig(): Promise<any> {
    return this.request('/system/config');
  }

  async healthCheck(): Promise<any> {
    return this.request('/health');
  }

  // Utilitários
  formatCurrency(value: number): string {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  }

  formatDate(dateString: string): string {
    return new Intl.DateTimeFormat('pt-BR').format(new Date(dateString));
  }

  formatDateTime(dateString: string): string {
    return new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(dateString));
  }
}

// Instância singleton
export const apiClient = new ApiClient(API_BASE_URL);

// Hooks personalizados para React Query (opcional)
export const useApi = () => {
  return apiClient;
};