// Arquivo: frontend/src/types/index.ts

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: 'admin' | 'gestor' | 'auditor' | 'operador';
  is_active: boolean;
  institution_id?: number;
}

export interface Institution {
  id: number;
  name: string;
  cnpj: string;
  type: string;
  status: 'active' | 'pending_approval' | 'suspended' | 'inactive';
  city: string;
  state: string;
  created_at: string;
}

export interface Project {
    id: number;
    title: string;
    status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected';
    institution_id: number;
    total_budget: number;
    start_date: string;
    end_date: string;
    created_at: string;
}

export interface ApiError {
  message: string;
}

// TIPO ADICIONADO AQUI
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  user: User;
}