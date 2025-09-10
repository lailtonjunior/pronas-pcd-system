/**
 * Definições de tipos baseadas nas regras PRONAS/PCD
 */

export interface Institution {
  id: number;
  cnpj: string;
  name: string;
  legal_name: string;
  institution_type: InstitutionType;
  cep: string;
  address: string;
  city: string;
  state: string;
  phone?: string;
  email: string;
  website?: string;
  legal_representative: string;
  legal_representative_cpf?: string;
  technical_responsible?: string;
  technical_responsible_registration?: string;
  experience_proof?: string;
  services_offered?: string;
  technical_capacity?: string;
  partnership_history?: string;
  credential_status: CredentialStatus;
  credential_date?: string;
  credential_expiry?: string;
  credential_number?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
}

export interface Project {
  id: number;
  institution_id: number;
  title: string;
  description?: string;
  field_of_action: FieldOfAction;
  priority_area_id: number;
  general_objective: string;
  specific_objectives: string[];
  justification: string;
  target_audience?: string;
  methodology?: string;
  expected_results?: string;
  sustainability_plan?: string;
  budget_total: number;
  budget_captacao?: number;
  budget_captacao_percentage?: number;
  timeline_months: number;
  start_date?: string;
  end_date?: string;
  status: ProjectStatus;
  submission_date?: string;
  approval_date?: string;
  execution_start_date?: string;
  execution_end_date?: string;
  evaluation_score?: number;
  compliance_score?: number;
  reviewer_comments?: string;
  created_at: string;
  updated_at?: string;
  created_by?: string;
  institution?: Institution;
  team_members?: ProjectTeam[];
  budget_items?: ProjectBudget[];
  goals?: ProjectGoal[];
  timeline?: ProjectTimeline[];
}

export interface ProjectTeam {
  id: number;
  project_id: number;
  role: string;
  name: string;
  cpf?: string;
  qualification: string;
  registration_number?: string;
  weekly_hours: number;
  monthly_salary?: number;
  start_date?: string;
  end_date?: string;
  created_at: string;
}

export interface ProjectBudget {
  id: number;
  project_id: number;
  category: BudgetCategory;
  subcategory?: string;
  description: string;
  unit?: string;
  quantity: number;
  unit_value: number;
  total_value: number;
  nature_expense_code?: string;
  justification?: string;
  created_at: string;
}

export interface ProjectGoal {
  id: number;
  project_id: number;
  indicator_name: string;
  target_value: number;
  measurement_method: string;
  frequency: MonitoringFrequency;
  baseline_value?: number;
  current_value?: number;
  created_at: string;
}

export interface ProjectTimeline {
  id: number;
  project_id: number;
  phase_name: string;
  start_month: number;
  end_month: number;
  deliverables?: string[];
  status?: string;
  completion_percentage?: number;
  created_at: string;
}

export interface PriorityArea {
  id: number;
  code: string;
  name: string;
  description?: string;
  requirements?: Record<string, any>;
  typical_actions?: string[];
  budget_guidelines?: Record<string, any>;
  team_guidelines?: Record<string, any>;
  active: boolean;
  created_at: string;
}

export interface AIProjectResponse {
  project: Record<string, any>;
  confidence_score: number;
  compliance_score: number;
  recommendations: string[];
  validation_results: Record<string, any>;
  similar_projects?: Record<string, any>[];
  generation_time?: number;
}

export interface ProjectValidation {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  compliance_score: number;
  required_documents: string[];
  missing_documents: string[];
  validation_details?: Record<string, any>;
}

export interface DashboardData {
  institutions: {
    total: number;
    active: number;
    pending: number;
    inactive: number;
  };
  projects: {
    total: number;
    draft: number;
    submitted: number;
    approved: number;
    in_execution: number;
    completed: number;
  };
  budget: {
    total_requested: number;
    total_approved: number;
  };
  by_priority_area: Record<string, number>;
  generated_at: string;
}

// Enums
export enum InstitutionType {
  HOSPITAL = 'hospital',
  APAE = 'apae',
  ONG = 'ong',
  FUNDACAO = 'fundacao',
  ASSOCIACAO = 'associacao',
  INSTITUTO = 'instituto',
  COOPERATIVA = 'cooperativa',
  OSCIP = 'oscip'
}

export enum CredentialStatus {
  PENDING = 'pending',
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  EXPIRED = 'expired',
  REJECTED = 'rejected'
}

export enum ProjectStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  IN_EXECUTION = 'in_execution',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

export enum FieldOfAction {
  MEDICO_ASSISTENCIAL = 'medico_assistencial',
  FORMACAO = 'formacao',
  PESQUISA = 'pesquisa'
}

export enum BudgetCategory {
  PESSOAL = 'pessoal',
  MATERIAL_CONSUMO = 'material_consumo',
  MATERIAL_PERMANENTE = 'material_permanente',
  DESPESAS_ADMINISTRATIVAS = 'despesas_administrativas',
  REFORMAS = 'reformas',
  CAPTACAO_RECURSOS = 'captacao_recursos',
  AUDITORIA = 'auditoria'
}

export enum MonitoringFrequency {
  MENSAL = 'mensal',
  TRIMESTRAL = 'trimestral',
  SEMESTRAL = 'semestral',
  ANUAL = 'anual'
}

// Formulários
export interface InstitutionFormData {
  cnpj: string;
  name: string;
  legal_name: string;
  institution_type: InstitutionType;
  cep: string;
  address: string;
  city: string;
  state: string;
  phone?: string;
  email: string;
  website?: string;
  legal_representative: string;
  legal_representative_cpf?: string;
  technical_responsible?: string;
  technical_responsible_registration?: string;
  experience_proof?: string;
  services_offered?: string;
  technical_capacity?: string;
  partnership_history?: string;
}

export interface ProjectGenerationRequest {
  institution_id: number;
  priority_area_code: string;
  budget_total: number;
  timeline_months?: number;
  target_beneficiaries?: number;
  local_context?: string;
}

export interface User {
  username: string;
  permissions: string[];
  authenticated: boolean;
  login_time?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  success: boolean;
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  timestamp?: string;
}

export interface ApiError {
  success: false;
  message: string;
  error_code?: string;
  error_type?: string;
  details?: Record<string, any>;
  timestamp: string;
}