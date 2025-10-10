// Arquivo: frontend/src/components/forms/ProjectForm.tsx
"use client";

import React, { useState, useEffect } from 'react';
import { useForm, Controller, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Plus, Trash2, Save, Send, AlertCircle, CheckCircle, Users, Calculator, Target, Calendar, FileText } from 'lucide-react';
import { apiClient } from '@/lib/api';
import { Institution, Project } from '@/types'; // Corrigido
import toast from 'react-hot-toast';

// Adicionando o tipo PriorityArea que estava faltando
interface PriorityArea {
  id: number;
  code: string;
  name: string;
}

// Schema de validação PRONAS/PCD
const projectSchema = z.object({
  institution_id: z.coerce.number().min(1, 'Selecione uma instituição'),
  priority_area_id: z.coerce.number().min(1, 'Selecione uma área prioritária'),
  title: z.string().min(10, 'Título deve ter pelo menos 10 caracteres').max(255),
  description: z.string().min(50, 'Descrição deve ter pelo menos 50 caracteres').optional(),
  field_of_action: z.enum(['medico_assistencial', 'formacao', 'pesquisa']),
  general_objective: z.string().min(50, 'Objetivo geral deve ter pelo menos 50 caracteres'),
  specific_objectives: z.array(z.object({ value: z.string().min(20) })).min(3, 'Mínimo de 3 objetivos específicos'),
  justification: z.string().min(500, 'Justificativa deve ter pelo menos 500 caracteres'),
  target_audience: z.string().min(20, 'Público-alvo deve ter pelo menos 20 caracteres').optional(),
  methodology: z.string().min(50, 'Metodologia deve ter pelo menos 50 caracteres').optional(),
  expected_results: z.string().min(50, 'Resultados esperados devem ter pelo menos 50 caracteres').optional(),
  budget_total: z.coerce.number().min(100000, 'Orçamento mínimo de R$ 100.000').max(5000000),
  timeline_months: z.coerce.number().min(6, 'Prazo mínimo de 6 meses').max(48, 'Prazo máximo de 48 meses'),
  estimated_beneficiaries: z.coerce.number().min(1),
});

type ProjectFormData = z.infer<typeof projectSchema>;

interface ProjectFormProps {
  project?: Partial<Project>;
  institutions: Institution[];
  priorityAreas: PriorityArea[];
  onSubmit: (data: ProjectFormData) => void;
  isLoading?: boolean;
}

export default function ProjectForm({
  project,
  institutions,
  priorityAreas,
  onSubmit,
  isLoading
}: ProjectFormProps) {
  const router = useRouter();

  const { control, handleSubmit, formState: { errors }, watch, setValue } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      institution_id: project?.institution_id || 0,
      title: project?.title || '',
      // ... outros valores padrão
      specific_objectives: [{ value: '' }, { value: '' }, { value: '' }],
    }
  });

  const { fields: objectiveFields, append: appendObjective, remove: removeObjective } = useFieldArray({
    control,
    name: "specific_objectives"
  });

  return (
      <Card>
        <CardHeader>
          <CardTitle>Formulário de Projeto</CardTitle>
          <CardDescription>Preencha os dados do projeto.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
             {/* Conteúdo do formulário aqui */}
             <Button type="submit" disabled={isLoading}>{isLoading ? 'Salvando...' : 'Salvar Projeto'}</Button>
          </form>
        </CardContent>
      </Card>
  );
}