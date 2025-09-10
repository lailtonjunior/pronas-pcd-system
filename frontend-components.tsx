# package.json - Frontend Dependencies for PRONAS/PCD System
{
  "name": "pronas-pcd-frontend",
  "version": "1.0.0",
  "description": "Frontend para o Sistema PRONAS/PCD - Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  },
  "dependencies": {
    "next": "14.0.3",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.2.2",
    "@types/node": "^20.8.7",
    "@types/react": "^18.2.31",
    "@types/react-dom": "^18.2.14",
    
    "tailwindcss": "^3.3.5",
    "@tailwindcss/forms": "^0.5.6",
    "@tailwindcss/typography": "^0.5.10",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-dropdown-menu": "^2.0.6",
    "@radix-ui/react-form": "^0.0.3",
    "@radix-ui/react-icons": "^1.3.0",
    "@radix-ui/react-label": "^2.0.2",
    "@radix-ui/react-select": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.4",
    "@radix-ui/react-toast": "^1.1.5",
    "@radix-ui/react-tooltip": "^1.0.7",
    
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0",
    "lucide-react": "^0.288.0",
    
    "react-hook-form": "^7.47.0",
    "@hookform/resolvers": "^3.3.2",
    "zod": "^3.22.4",
    
    "axios": "^1.5.1",
    "@tanstack/react-query": "^5.6.2",
    
    "date-fns": "^2.30.0",
    "react-datepicker": "^4.21.0",
    
    "react-dropzone": "^14.2.3",
    "file-saver": "^2.0.5",
    
    "recharts": "^2.8.0",
    "react-pdf": "^7.5.1",
    
    "next-auth": "^4.24.4",
    "@next-auth/prisma-adapter": "^1.0.7",
    
    "react-table": "^7.8.0",
    "@types/react-table": "^7.7.17",
    
    "framer-motion": "^10.16.4",
    
    "currency-formatter": "^1.5.9",
    "react-input-mask": "^2.0.4"
  },
  "devDependencies": {
    "eslint": "^8.51.0",
    "eslint-config-next": "14.0.3",
    "@typescript-eslint/eslint-plugin": "^6.8.0",
    "@typescript-eslint/parser": "^6.8.0",
    
    "prettier": "^3.0.3",
    "prettier-plugin-tailwindcss": "^0.5.6",
    
    "jest": "^29.7.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.4",
    "jest-environment-jsdom": "^29.7.0",
    
    "@types/file-saver": "^2.0.7"
  }
}


---

# src/types/pronas.ts - TypeScript Types
export interface Institution {
  id: number;
  cnpj: string;
  name: string;
  legalName: string;
  institutionType: 'hospital' | 'apae' | 'ong' | 'fundacao' | 'associacao' | 'instituto';
  cep: string;
  address: string;
  city: string;
  state: string;
  phone?: string;
  email: string;
  legalRepresentative: string;
  technicalResponsible?: string;
  experienceProof?: string;
  credentialStatus: 'pending' | 'active' | 'inactive' | 'expired' | 'rejected';
  credentialDate?: string;
  credentialExpiry?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface Project {
  id: number;
  institutionId: number;
  title: string;
  description?: string;
  fieldOfAction: 'medico_assistencial' | 'formacao' | 'pesquisa';
  priorityAreaId: number;
  generalObjective: string;
  specificObjectives: string[];
  justification: string;
  targetAudience?: string;
  methodology?: string;
  expectedResults?: string;
  budgetTotal: number;
  timelineMonths: number;
  status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'in_execution' | 'completed' | 'cancelled';
  submissionDate?: string;
  approvalDate?: string;
  executionStartDate?: string;
  executionEndDate?: string;
  createdAt: string;
  updatedAt?: string;
  
  // Relacionamentos
  institution?: Institution;
  teamMembers?: ProjectTeam[];
  budgetItems?: ProjectBudget[];
  goals?: ProjectGoal[];
  timeline?: ProjectTimeline[];
}

export interface ProjectTeam {
  id: number;
  projectId: number;
  role: string;
  name: string;
  cpf?: string;
  qualification: string;
  weeklyHours: number;
  monthlySalary?: number;
  createdAt: string;
}

export interface ProjectBudget {
  id: number;
  projectId: number;
  category: 'pessoal' | 'material_consumo' | 'material_permanente' | 'despesas_administrativas' | 'reformas' | 'captacao_recursos' | 'auditoria' | 'outros';
  subcategory?: string;
  description: string;
  unit?: string;
  quantity: number;
  unitValue: number;
  totalValue: number;
  natureExpenseCode?: string;
  createdAt: string;
}

export interface ProjectGoal {
  id: number;
  projectId: number;
  indicatorName: string;
  targetValue: number;
  measurementMethod: string;
  frequency: 'mensal' | 'trimestral' | 'semestral' | 'anual';
  baselineValue?: number;
  createdAt: string;
}

export interface ProjectTimeline {
  id: number;
  projectId: number;
  phaseName: string;
  startMonth: number;
  endMonth: number;
  deliverables?: string[];
  createdAt: string;
}

export interface PriorityArea {
  id: number;
  code: string;
  name: string;
  description?: string;
  requirements?: Record<string, any>;
  active: boolean;
}

export interface AIProjectResponse {
  project: Partial<Project>;
  confidenceScore: number;
  complianceScore: number;
  recommendations: string[];
  validationResults: Record<string, any>;
  similarProjects?: Record<string, any>[];
}

export interface ProjectValidation {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  complianceScore: number;
  requiredDocuments: string[];
  missingDocuments: string[];
}


---

# src/components/ui/button.tsx - Reusable Button Component
"use client";

import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        pronas: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
        success: "bg-green-600 text-white hover:bg-green-700 focus:ring-green-500",
        warning: "bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500"
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };


---

# src/components/institutions/InstitutionForm.tsx - Institution Form Component
"use client";

import React from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Institution } from '@/types/pronas';

// Schema de validação baseado nas regras do PRONAS/PCD
const institutionSchema = z.object({
  cnpj: z.string()
    .regex(/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/, 'CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX')
    .min(1, 'CNPJ é obrigatório'),
  name: z.string()
    .min(3, 'Nome deve ter pelo menos 3 caracteres')
    .max(255, 'Nome não pode exceder 255 caracteres'),
  legalName: z.string()
    .min(3, 'Razão social deve ter pelo menos 3 caracteres')
    .max(255, 'Razão social não pode exceder 255 caracteres'),
  institutionType: z.enum(['hospital', 'apae', 'ong', 'fundacao', 'associacao', 'instituto']),
  cep: z.string()
    .regex(/^\d{5}-\d{3}$/, 'CEP deve estar no formato XXXXX-XXX'),
  address: z.string()
    .min(10, 'Endereço deve ter pelo menos 10 caracteres')
    .max(500, 'Endereço não pode exceder 500 caracteres'),
  city: z.string()
    .min(2, 'Cidade deve ter pelo menos 2 caracteres')
    .max(100, 'Cidade não pode exceder 100 caracteres'),
  state: z.string()
    .regex(/^[A-Z]{2}$/, 'UF deve ter exatamente 2 letras maiúsculas'),
  phone: z.string()
    .regex(/^\(\d{2}\) \d{4,5}-\d{4}$/, 'Telefone deve estar no formato (XX) XXXXX-XXXX')
    .optional(),
  email: z.string()
    .email('Email deve ser válido'),
  legalRepresentative: z.string()
    .min(3, 'Representante legal deve ter pelo menos 3 caracteres')
    .max(255, 'Representante legal não pode exceder 255 caracteres'),
  technicalResponsible: z.string()
    .max(255, 'Responsável técnico não pode exceder 255 caracteres')
    .optional(),
  experienceProof: z.string()
    .min(50, 'Comprovação de experiência deve ter pelo menos 50 caracteres')
    .optional()
});

type InstitutionFormData = z.infer<typeof institutionSchema>;

interface InstitutionFormProps {
  institution?: Partial<Institution>;
  onSubmit: (data: InstitutionFormData) => Promise<void>;
  isLoading?: boolean;
}

const institutionTypeOptions = [
  { value: 'hospital', label: 'Hospital' },
  { value: 'apae', label: 'APAE' },
  { value: 'ong', label: 'ONG' },
  { value: 'fundacao', label: 'Fundação' },
  { value: 'associacao', label: 'Associação' },
  { value: 'instituto', label: 'Instituto' }
];

const stateOptions = [
  'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 
  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
].map(state => ({ value: state, label: state }));

export default function InstitutionForm({ institution, onSubmit, isLoading = false }: InstitutionFormProps) {
  const { control, handleSubmit, formState: { errors }, watch, setValue } = useForm<InstitutionFormData>({
    resolver: zodResolver(institutionSchema),
    defaultValues: {
      cnpj: institution?.cnpj || '',
      name: institution?.name || '',
      legalName: institution?.legalName || '',
      institutionType: institution?.institutionType || 'apae',
      cep: institution?.cep || '',
      address: institution?.address || '',
      city: institution?.city || '',
      state: institution?.state || '',
      phone: institution?.phone || '',
      email: institution?.email || '',
      legalRepresentative: institution?.legalRepresentative || '',
      technicalResponsible: institution?.technicalResponsible || '',
      experienceProof: institution?.experienceProof || ''
    }
  });

  // Auto-buscar endereço pelo CEP
  const cepValue = watch('cep');
  React.useEffect(() => {
    if (cepValue && cepValue.match(/^\d{5}-\d{3}$/)) {
      fetch(`https://viacep.com.br/ws/${cepValue.replace('-', '')}/json/`)
        .then(response => response.json())
        .then(data => {
          if (!data.erro) {
            setValue('address', data.logradouro);
            setValue('city', data.localidade);
            setValue('state', data.uf);
          }
        })
        .catch(console.error);
    }
  }, [cepValue, setValue]);

  const onSubmitForm = async (data: InstitutionFormData) => {
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Erro ao salvar instituição:', error);
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle>
          {institution ? 'Editar Instituição' : 'Cadastrar Nova Instituição'}
        </CardTitle>
        <CardDescription>
          Preencha os dados da instituição conforme exigido pelo PRONAS/PCD. 
          Todos os campos marcados com (*) são obrigatórios.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit(onSubmitForm)} className="space-y-6">
          {/* Informações Básicas */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Informações Básicas</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="cnpj">CNPJ *</Label>
                <Controller
                  name="cnpj"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="cnpj"
                      placeholder="XX.XXX.XXX/XXXX-XX"
                      className={errors.cnpj ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.cnpj && (
                  <p className="text-sm text-red-500 mt-1">{errors.cnpj.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="institutionType">Tipo de Instituição *</Label>
                <Controller
                  name="institutionType"
                  control={control}
                  render={({ field }) => (
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      {institutionTypeOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Select>
                  )}
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="name">Nome Fantasia *</Label>
              <Controller
                name="name"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    id="name"
                    placeholder="Nome como é conhecida"
                    className={errors.name ? 'border-red-500' : ''}
                  />
                )}
              />
              {errors.name && (
                <p className="text-sm text-red-500 mt-1">{errors.name.message}</p>
              )}
            </div>
            
            <div>
              <Label htmlFor="legalName">Razão Social *</Label>
              <Controller
                name="legalName"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    id="legalName"
                    placeholder="Razão social conforme CNPJ"
                    className={errors.legalName ? 'border-red-500' : ''}
                  />
                )}
              />
              {errors.legalName && (
                <p className="text-sm text-red-500 mt-1">{errors.legalName.message}</p>
              )}
            </div>
          </div>

          {/* Endereço */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Endereço</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="cep">CEP *</Label>
                <Controller
                  name="cep"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="cep"
                      placeholder="XXXXX-XXX"
                      className={errors.cep ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.cep && (
                  <p className="text-sm text-red-500 mt-1">{errors.cep.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="city">Cidade *</Label>
                <Controller
                  name="city"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="city"
                      placeholder="Cidade"
                      className={errors.city ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.city && (
                  <p className="text-sm text-red-500 mt-1">{errors.city.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="state">UF *</Label>
                <Controller
                  name="state"
                  control={control}
                  render={({ field }) => (
                    <Select
                      value={field.value}
                      onValueChange={field.onChange}
                    >
                      {stateOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Select>
                  )}
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="address">Endereço Completo *</Label>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    id="address"
                    placeholder="Logradouro, número, complemento, bairro"
                    className={errors.address ? 'border-red-500' : ''}
                  />
                )}
              />
              {errors.address && (
                <p className="text-sm text-red-500 mt-1">{errors.address.message}</p>
              )}
            </div>
          </div>

          {/* Contato */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Contato</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="email">Email *</Label>
                <Controller
                  name="email"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="email"
                      type="email"
                      placeholder="email@instituicao.org.br"
                      className={errors.email ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.email && (
                  <p className="text-sm text-red-500 mt-1">{errors.email.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="phone">Telefone</Label>
                <Controller
                  name="phone"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="phone"
                      placeholder="(XX) XXXXX-XXXX"
                      className={errors.phone ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.phone && (
                  <p className="text-sm text-red-500 mt-1">{errors.phone.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Responsáveis */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Responsáveis</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="legalRepresentative">Representante Legal *</Label>
                <Controller
                  name="legalRepresentative"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="legalRepresentative"
                      placeholder="Nome do representante legal"
                      className={errors.legalRepresentative ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.legalRepresentative && (
                  <p className="text-sm text-red-500 mt-1">{errors.legalRepresentative.message}</p>
                )}
              </div>
              
              <div>
                <Label htmlFor="technicalResponsible">Responsável Técnico</Label>
                <Controller
                  name="technicalResponsible"
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      id="technicalResponsible"
                      placeholder="Nome do responsável técnico"
                      className={errors.technicalResponsible ? 'border-red-500' : ''}
                    />
                  )}
                />
                {errors.technicalResponsible && (
                  <p className="text-sm text-red-500 mt-1">{errors.technicalResponsible.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Experiência */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">Comprovação de Experiência</h3>
            
            <div>
              <Label htmlFor="experienceProof">
                Descrição da Experiência (mínimo 50 caracteres)
              </Label>
              <Controller
                name="experienceProof"
                control={control}
                render={({ field }) => (
                  <Textarea
                    {...field}
                    id="experienceProof"
                    rows={4}
                    placeholder="Descreva a experiência da instituição na área de saúde da pessoa com deficiência, incluindo tempo de atuação, serviços oferecidos, profissionais especializados, parcerias, etc."
                    className={errors.experienceProof ? 'border-red-500' : ''}
                  />
                )}
              />
              {errors.experienceProof && (
                <p className="text-sm text-red-500 mt-1">{errors.experienceProof.message}</p>
              )}
            </div>
          </div>

          {/* Alerta sobre credenciamento */}
          <Alert>
            <AlertDescription>
              <strong>Importante:</strong> O credenciamento no PRONAS/PCD deve ser solicitado 
              apenas nos meses de junho e julho de cada ano. Após o preenchimento deste 
              formulário, será necessário anexar os documentos obrigatórios conforme 
              especificado na Portaria de Consolidação nº 5/2017.
            </AlertDescription>
          </Alert>

          {/* Botões */}
          <div className="flex justify-end space-x-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => window.history.back()}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="pronas"
              disabled={isLoading}
            >
              {isLoading ? 'Salvando...' : 'Salvar Instituição'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}