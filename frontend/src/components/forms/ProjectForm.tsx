"use client";

import React, { useState, useEffect } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { 
  Card, CardContent, CardDescription, CardHeader, CardTitle 
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Plus, Trash2, Save, Send, AlertCircle, CheckCircle, 
  Users, Calculator, Target, Calendar, FileText 
} from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Institution, PriorityArea, Project } from '@/types/pronas';
import toast from 'react-hot-toast';

// Schema de validação PRONAS/PCD
const projectSchema = z.object({
  institution_id: z.number().min(1, 'Selecione uma instituição'),
  priority_area_id: z.number().min(1, 'Selecione uma área prioritária'),
  title: z.string().min(10, 'Título deve ter pelo menos 10 caracteres').max(255),
  description: z.string().min(50, 'Descrição deve ter pelo menos 50 caracteres').optional(),
  field_of_action: z.enum(['medico_assistencial', 'formacao', 'pesquisa']),
  
  general_objective: z.string().min(50, 'Objetivo geral deve ter pelo menos 50 caracteres'),
  specific_objectives: z.array(z.string().min(20)).min(3, 'Mínimo de 3 objetivos específicos'),
  
  justification: z.string().min(500, 'Justificativa deve ter pelo menos 500 caracteres'),
  target_audience: z.string().min(20, 'Público-alvo deve ter pelo menos 20 caracteres').optional(),
  methodology: z.string().min(50, 'Metodologia deve ter pelo menos 50 caracteres').optional(),
  expected_results: z.string().min(50, 'Resultados esperados devem ter pelo menos 50 caracteres').optional(),
  sustainability_plan: z.string().optional(),
  
  budget_total: z.number().min(100000, 'Orçamento mínimo de R$ 100.000').max(5000000),
  timeline_months: z.number().min(6, 'Prazo mínimo de 6 meses').max(48, 'Prazo máximo de 48 meses'),
  estimated_beneficiaries: z.number().min(1),
  
  execution_city: z.string().optional(),
  execution_state: z.string().length(2).optional(),
  
  // Arrays complexos
  team_members: z.array(z.object({
    role: z.string().min(3),
    name: z.string().min(3),
    cpf: z.string().optional(),
    qualification: z.string().min(10),
    weekly_hours: z.number().min(1).max(44),
    monthly_salary: z.number().optional()
  })).min(2, 'Equipe deve ter pelo menos 2 profissionais'),
  
  budget_items: z.array(z.object({
    category: z.string(),
    subcategory: z.string().optional(),
    description: z.string().min(3),
    unit: z.string().optional(),
    quantity: z.number().min(1),
    unit_value: z.number().min(0),
    total_value: z.number().min(0),
    nature_expense_code: z.string().optional(),
    justification: z.string().optional()
  })).min(1, 'Orçamento deve ter pelo menos 1 item'),
  
  goals: z.array(z.object({
    indicator_name: z.string().min(3),
    target_value: z.number().min(0),
    measurement_method: z.string().min(10),
    frequency: z.enum(['mensal', 'trimestral', 'semestral', 'anual']),
    baseline_value: z.number().optional()
  })).min(2, 'Projeto deve ter pelo menos 2 metas/indicadores'),
  
  timeline: z.array(z.object({
    phase_name: z.string().min(3),
    start_month: z.number().min(1),
    end_month: z.number().min(1),
    deliverables: z.array(z.string())
  })).min(3, 'Cronograma deve ter pelo menos 3 fases')
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  project?: Partial<Project>;
  institutions: Institution[];
  priorityAreas: PriorityArea[];
  onSubmit?: (data: ProjectFormData) => Promise<void>;
}

export default function ProjectForm({ 
  project, 
  institutions, 
  priorityAreas,
  onSubmit 
}: ProjectFormProps) {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [validationScore, setValidationScore] = useState(0);
  const [activeTab, setActiveTab] = useState('basic');

  const { control, handleSubmit, formState: { errors }, watch, setValue, trigger } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      institution_id: project?.institution_id || 0,
      priority_area_id: project?.priority_area_id || 0,
      title: project?.title || '',
      description: project?.description || '',
      field_of_action: project?.field_of_action || 'medico_assistencial',
      general_objective: project?.general_objective || '',
      specific_objectives: project?.specific_objectives || ['', '', ''],
      justification: project?.justification || '',
      target_audience: project?.target_audience || '',
      methodology: project?.methodology || '',
      expected_results: project?.expected_results || '',
      sustainability_plan: project?.sustainability_plan || '',
      budget_total: project?.budget_total || 500000,
      timeline_months: project?.timeline_months || 24,
      estimated_beneficiaries: project?.estimated_beneficiaries || 100,
      execution_city: project?.execution_city || '',
      execution_state: project?.execution_state || '',
      team_members: project?.team_members || [
        { role: '', name: '', qualification: '', weekly_hours: 20, monthly_salary: 0 }
      ],
      budget_items: project?.budget_items || [
        { category: 'pessoal', description: '', quantity: 1, unit_value: 0, total_value: 0 }
      ],
      goals: project?.goals || [
        { indicator_name: '', target_value: 0, measurement_method: '', frequency: 'trimestral' }
      ],
      timeline: project?.timeline || [
        { phase_name: 'Planejamento', start_month: 1, end_month: 3, deliverables: [] }
      ]
    }
  });

  const { fields: objectiveFields, append: appendObjective, remove: removeObjective } = useFieldArray({
    control,
    name: "specific_objectives"
  });

  const { fields: teamFields, append: appendTeam, remove: removeTeam } = useFieldArray({
    control,
    name: "team_members"
  });

  const { fields: budgetFields, append: appendBudget, remove: removeBudget } = useFieldArray({
    control,
    name: "budget_items"
  });

  const { fields: goalFields, append: appendGoal, remove: removeGoal } = useFieldArray({
    control,
    name: "goals"
  });

  const { fields: timelineFields, append: appendTimeline, remove: removeTimeline } = useFieldArray({
    control,
    name: "timeline"
  });

  // Watch para cálculos automáticos
  const budgetItems = watch('budget_items');
  const timelineMonths = watch('timeline_months');
  const priorityAreaId = watch('priority_area_id');

  // Calcular total do orçamento automaticamente
  useEffect(() => {
    const total = budgetItems.reduce((acc, item) => {
      return acc + (item.total_value || 0);
    }, 0);
    setValue('budget_total', total);
  }, [budgetItems, setValue]);

  // Validar conformidade com PRONAS/PCD
  const validateCompliance = async () => {
    const isValid = await trigger();
    
    if (isValid) {
      // Verificar requisitos específicos
      let score = 100;
      const issues = [];
      
      // Verificar auditoria obrigatória
      const hasAudit = budgetItems.some(item => item.category === 'auditoria');
      if (!hasAudit) {
        score -= 20;
        issues.push('Auditoria independente é obrigatória');
      }
      
      // Verificar captação de recursos
      const captacaoItems = budgetItems.filter(item => item.category === 'captacao_recursos');
      const captacaoTotal = captacaoItems.reduce((acc, item) => acc + item.total_value, 0);
      const budgetTotal = watch('budget_total');
      
      if (captacaoTotal > Math.min(budgetTotal * 0.05, 50000)) {
        score -= 15;
        issues.push('Captação de recursos excede limite (5% ou R$ 50.000)');
      }
      
      // Verificar consistência do cronograma
      const maxMonth = Math.max(...timelineFields.map(f => f.end_month));
      if (maxMonth > timelineMonths) {
        score -= 10;
        issues.push('Cronograma excede prazo do projeto');
      }
      
      setValidationScore(score);
      
      if (issues.length > 0) {
        toast.error('Problemas de conformidade:\n' + issues.join('\n'));
      } else {
        toast.success('Projeto em conformidade com PRONAS/PCD!');
      }
    }
  };

  const onSubmitForm = async (data: ProjectFormData) => {
    try {
      setIsSubmitting(true);
      
      // Validar conformidade antes de enviar
      await validateCompliance();
      
      if (validationScore < 70) {
        const confirm = window.confirm(
          'O projeto tem problemas de conformidade. Deseja salvar como rascunho?'
        );
        if (!confirm) {
          setIsSubmitting(false);
          return;
        }
      }
      
      if (onSubmit) {
        await onSubmit(data);
      } else {
        // Chamada API padrão
        if (project?.id) {
          await apiClient.updateProject(project.id, data);
          toast.success('Projeto atualizado com sucesso!');
        } else {
          await apiClient.createProject(data);
          toast.success('Projeto criado com sucesso!');
        }
        
        router.push('/dashboard/projects');
      }
    } catch (error: any) {
      toast.error(error.message || 'Erro ao salvar projeto');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitForApproval = async () => {
    const isValid = await trigger();
    
    if (!isValid) {
      toast.error('Corrija os erros antes de submeter o projeto');
      return;
    }
    
    if (validationScore < 80) {
      toast.error('Projeto precisa ter pelo menos 80% de conformidade para submissão');
      return;
    }
    
    try {
      setIsSubmitting(true);
      
      const data = watch();
      const projectId = await apiClient.createProject(data);
      await apiClient.submitProject(projectId);
      
      toast.success('Projeto submetido para análise do Ministério da Saúde!');
      router.push('/dashboard/projects');
    } catch (error: any) {
      toast.error(error.message || 'Erro ao submeter projeto');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{project ? 'Editar Projeto' : 'Novo Projeto PRONAS/PCD'}</span>
            <div className="flex items-center gap-4">
              <Badge variant={validationScore >= 80 ? 'success' : 'warning'}>
                Conformidade: {validationScore}%
              </Badge>
              <Progress value={validationScore} className="w-32" />
            </div>
          </CardTitle>
          <CardDescription>
            Preencha todos os campos obrigatórios seguindo as diretrizes da 
            Portaria de Consolidação nº 5/2017
          </CardDescription>
        </CardHeader>
        
        <CardContent>
          <form onSubmit={handleSubmit(onSubmitForm)}>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="basic">
                  <FileText className="mr-2 h-4 w-4" />
                  Dados Básicos
                </TabsTrigger>
                <TabsTrigger value="team">
                  <Users className="mr-2 h-4 w-4" />
                  Equipe
                </TabsTrigger>
                <TabsTrigger value="budget">
                  <Calculator className="mr-2 h-4 w-4" />
                  Orçamento
                </TabsTrigger>
                <TabsTrigger value="goals">
                  <Target className="mr-2 h-4 w-4" />
                  Metas
                </TabsTrigger>
                <TabsTrigger value="timeline">
                  <Calendar className="mr-2 h-4 w-4" />
                  Cronograma
                </TabsTrigger>
              </TabsList>

              {/* Tab: Dados Básicos */}
              <TabsContent value="basic" className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="institution_id">Instituição *</Label>
                    <Controller
                      name="institution_id"
                      control={control}
                      render={({ field }) => (
                        <Select
                          value={field.value.toString()}
                          onValueChange={(value) => field.onChange(parseInt(value))}
                        >
                          <option value="0">Selecione uma instituição</option>
                          {institutions.map(inst => (
                            <option key={inst.id} value={inst.id}>
                              {inst.name}
                            </option>
                          ))}
                        </Select>
                      )}
                    />
                    {errors.institution_id && (
                      <p className="text-sm text-red-500 mt-1">{errors.institution_id.message}</p>
                    )}
                  </div>

                  <div>
                    <Label htmlFor="priority_area_id">Área Prioritária *</Label>
                    <Controller
                      name="priority_area_id"
                      control={control}
                      render={({ field }) => (
                        <Select
                          value={field.value.toString()}
                          onValueChange={(value) => field.onChange(parseInt(value))}
                        >
                          <option value="0">Selecione uma área</option>
                          {priorityAreas.map(area => (
                            <option key={area.id} value={area.id}>
                              {area.code} - {area.name}
                            </option>
                          ))}
                        </Select>
                      )}
                    />
                    {errors.priority_area_id && (
                      <p className="text-sm text-red-500 mt-1">{errors.priority_area_id.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <Label htmlFor="title">Título do Projeto *</Label>
                  <Controller
                    name="title"
                    control={control}
                    render={({ field }) => (
                      <Input
                        {...field}
                        placeholder="Título claro e objetivo do projeto"
                        className={errors.title ? 'border-red-500' : ''}
                      />
                    )}
                  />
                  {errors.title && (
                    <p className="text-sm text-red-500 mt-1">{errors.title.message}</p>
                  )}
                </div>

                {/* Continue com os outros campos... */}
                
              </TabsContent>

              {/* Outras tabs seguem o mesmo padrão... */}

            </Tabs>

            {/* Botões de ação */}
            <div className="flex justify-between mt-8">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
              >
                Cancelar
              </Button>
              
              <div className="flex gap-4">
                <Button
                  type="button"
                  variant="secondary"
                  onClick={validateCompliance}
                >
                  <CheckCircle className="mr-2 h-4 w-4" />
                  Validar Conformidade
                </Button>
                
                <Button
                  type="submit"
                  variant="default"
                  disabled={isSubmitting}
                >
                  <Save className="mr-2 h-4 w-4" />
                  {isSubmitting ? 'Salvando...' : 'Salvar Rascunho'}
                </Button>
                
                {(!project || project.status === 'draft') && (
                  <Button
                    type="button"
                    variant="success"
                    onClick={handleSubmitForApproval}
                    disabled={isSubmitting || validationScore < 80}
                  >
                    <Send className="mr-2 h-4 w-4" />
                    Submeter ao MS
                  </Button>
                )}
              </div>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}