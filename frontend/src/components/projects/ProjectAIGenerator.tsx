/**
 * Componente para geração de projetos PRONAS/PCD usando IA especializada
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ProjectGenerationRequest, PriorityArea, Institution, AIProjectResponse } from '@/types/pronas';
import { useApi } from '@/lib/api';

// Schema de validação para geração de projeto
const projectGenerationSchema = z.object({
  institution_id: z.number().min(1, 'Selecione uma instituição'),
  priority_area_code: z.string().min(1, 'Selecione uma área prioritária'),
  budget_total: z.number()
    .min(50000, 'Orçamento mínimo é R$ 50.000')
    .max(10000000, 'Orçamento máximo é R$ 10.000.000'),
  timeline_months: z.number()
    .min(6, 'Prazo mínimo é 6 meses')
    .max(48, 'Prazo máximo é 48 meses')
    .optional(),
  target_beneficiaries: z.number()
    .min(10, 'Mínimo 10 beneficiários')
    .max(10000, 'Máximo 10.000 beneficiários')
    .optional(),
  local_context: z.string()
    .max(1000, 'Contexto local deve ter no máximo 1000 caracteres')
    .optional(),
});

type ProjectGenerationValues = z.infer<typeof projectGenerationSchema>;

interface ProjectAIGeneratorProps {
  onProjectGenerated?: (project: AIProjectResponse) => void;
  onCancel?: () => void;
}

export default function ProjectAIGenerator({
  onProjectGenerated,
  onCancel
}: ProjectAIGeneratorProps) {
  const api = useApi();
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [priorityAreas, setPriorityAreas] = useState<PriorityArea[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [generatedProject, setGeneratedProject] = useState<AIProjectResponse | null>(null);
  const [selectedArea, setSelectedArea] = useState<PriorityArea | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<ProjectGenerationValues>({
    resolver: zodResolver(projectGenerationSchema),
    defaultValues: {
      timeline_months: 24,
      target_beneficiaries: 200,
    },
  });

  // Carregar dados iniciais
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [institutionsResponse, areasResponse] = await Promise.all([
          api.getInstitutions({ credential_status: 'active' }),
          api.getPriorityAreas()
        ]);

        setInstitutions(institutionsResponse || []);
        setPriorityAreas(areasResponse || []);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
      }
    };

    loadInitialData();
  }, [api]);

  // Monitorar área selecionada
  const watchedAreaCode = watch('priority_area_code');
  useEffect(() => {
    const area = priorityAreas.find(a => a.code === watchedAreaCode);
    setSelectedArea(area || null);
  }, [watchedAreaCode, priorityAreas]);

  const handleFormSubmit: SubmitHandler<ProjectGenerationValues> = async (data) => {
    setIsGenerating(true);
    setGenerationError(null);
    setGeneratedProject(null);

    try {
      const response = await api.generateProject(data);
      setGeneratedProject(response);
      
      if (onProjectGenerated) {
        onProjectGenerated(response);
      }
    } catch (error) {
      setGenerationError(
        error instanceof Error ? error.message : 'Erro ao gerar projeto'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const getComplianceColor = (score: number) => {
    if (score >= 0.9) return 'text-green-600 bg-green-100';
    if (score >= 0.7) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-blue-600 bg-blue-100';
    if (score >= 0.6) return 'text-indigo-600 bg-indigo-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Formulário de Geração */}
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Gerador Inteligente de Projetos PRONAS/PCD</h2>
          <p className="card-subtitle">
            Use IA especializada para gerar projetos conformes com as diretrizes oficiais do Ministério da Saúde
          </p>
        </div>

        {generationError && (
          <div className="alert alert-danger">
            <strong>Erro!</strong> {generationError}
          </div>
        )}

        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Coluna Esquerda */}
            <div className="space-y-4">
              {/* Instituição */}
              <div className="form-group">
                <label htmlFor="institution_id" className="form-label">
                  Instituição <span className="text-red-500">*</span>
                </label>
                <select
                  id="institution_id"
                  {...register('institution_id', { valueAsNumber: true })}
                  className={`form-select ${errors.institution_id ? 'border-red-500' : ''}`}
                >
                  <option value="">Selecione uma instituição credenciada</option>
                  {institutions.map(institution => (
                    <option key={institution.id} value={institution.id}>
                      {institution.name} - {institution.city}/{institution.state}
                    </option>
                  ))}
                </select>
                {errors.institution_id && <p className="form-error">{errors.institution_id.message}</p>}
              </div>

              {/* Área Prioritária */}
              <div className="form-group">
                <label htmlFor="priority_area_code" className="form-label">
                  Área Prioritária <span className="text-red-500">*</span>
                </label>
                <select
                  id="priority_area_code"
                  {...register('priority_area_code')}
                  className={`form-select ${errors.priority_area_code ? 'border-red-500' : ''}`}
                >
                  <option value="">Selecione uma área prioritária</option>
                  {priorityAreas.map(area => (
                    <option key={area.code} value={area.code}>
                      {area.code} - {area.name}
                    </option>
                  ))}
                </select>
                {errors.priority_area_code && <p className="form-error">{errors.priority_area_code.message}</p>}
              </div>

              {/* Orçamento Total */}
              <div className="form-group">
                <label htmlFor="budget_total" className="form-label">
                  Orçamento Total <span className="text-red-500">*</span>
                </label>
                <input
                  type="number"
                  id="budget_total"
                  {...register('budget_total', { valueAsNumber: true })}
                  className={`form-input ${errors.budget_total ? 'border-red-500' : ''}`}
                  placeholder="500000"
                  min="50000"
                  max="10000000"
                  step="1000"
                />
                {errors.budget_total && <p className="form-error">{errors.budget_total.message}</p>}
                <p className="form-help">Entre R$ 50.000 e R$ 10.000.000</p>
              </div>
            </div>

            {/* Coluna Direita */}
            <div className="space-y-4">
              {/* Prazo */}
              <div className="form-group">
                <label htmlFor="timeline_months" className="form-label">
                  Prazo (meses)
                </label>
                <input
                  type="number"
                  id="timeline_months"
                  {...register('timeline_months', { valueAsNumber: true })}
                  className={`form-input ${errors.timeline_months ? 'border-red-500' : ''}`}
                  placeholder="24"
                  min="6"
                  max="48"
                />
                {errors.timeline_months && <p className="form-error">{errors.timeline_months.message}</p>}
                <p className="form-help">Entre 6 e 48 meses (padrão: 24 meses)</p>
              </div>

              {/* Beneficiários */}
              <div className="form-group">
                <label htmlFor="target_beneficiaries" className="form-label">
                  Número de Beneficiários
                </label>
                <input
                  type="number"
                  id="target_beneficiaries"
                  {...register('target_beneficiaries', { valueAsNumber: true })}
                  className={`form-input ${errors.target_beneficiaries ? 'border-red-500' : ''}`}
                  placeholder="200"
                  min="10"
                  max="10000"
                />
                {errors.target_beneficiaries && <p className="form-error">{errors.target_beneficiaries.message}</p>}
                <p className="form-help">Número estimado de pessoas atendidas</p>
              </div>

              {/* Contexto Local */}
              <div className="form-group">
                <label htmlFor="local_context" className="form-label">
                  Contexto Local
                </label>
                <textarea
                  id="local_context"
                  {...register('local_context')}
                  className="form-textarea"
                  rows={3}
                  placeholder="Descreva particularidades da região, necessidades específicas, etc."
                  maxLength={1000}
                />
                <p className="form-help">Informações opcionais sobre o contexto local (máximo 1000 caracteres)</p>
              </div>
            </div>
          </div>

          {/* Informações da Área Selecionada */}
          {selectedArea && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">
                {selectedArea.code} - {selectedArea.name}
              </h3>
              <p className="text-blue-800 text-sm mb-3">{selectedArea.description}</p>
              
              {selectedArea.typical_actions && selectedArea.typical_actions.length > 0 && (
                <div>
                  <p className="font-medium text-blue-900 mb-2">Ações Típicas:</p>
                  <ul className="list-disc list-inside text-blue-800 text-sm space-y-1">
                    {selectedArea.typical_actions.slice(0, 3).map((action, index) => (
                      <li key={index}>{action}</li>
                    ))}
                    {selectedArea.typical_actions.length > 3 && (
                      <li className="italic">... e mais {selectedArea.typical_actions.length - 3} ações</li>
                    )}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Botões */}
          <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
            {onCancel && (
              <button
                type="button"
                onClick={onCancel}
                className="btn-outline"
                disabled={isGenerating}
              >
                Cancelar
              </button>
            )}
            
            <button
              type="submit"
              className="btn-primary"
              disabled={isGenerating}
            >
              {isGenerating ? (
                <>
                  <div className="spinner mr-2"></div>
                  Gerando Projeto...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Gerar Projeto com IA
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Resultado da Geração */}
      {generatedProject && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Projeto Gerado pela IA</h3>
            <div className="flex space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(generatedProject.confidence_score)}`}>
                Confiança: {(generatedProject.confidence_score * 100).toFixed(1)}%
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getComplianceColor(generatedProject.compliance_score)}`}>
                Conformidade: {(generatedProject.compliance_score * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Informações Principais */}
            <div className="lg:col-span-2 space-y-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Título do Projeto</h4>
                <p className="text-gray-800">{generatedProject.project.title}</p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Objetivo Geral</h4>
                <p className="text-gray-800">{generatedProject.project.general_objective}</p>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Objetivos Específicos</h4>
                <ul className="list-disc list-inside text-gray-800 space-y-1">
                  {generatedProject.project.specific_objectives?.map((objective: string, index: number) => (
                    <li key={index}>{objective}</li>
                  ))}
                </ul>
              </div>

              {generatedProject.project.justification && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Justificativa</h4>
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <p className="text-gray-800 text-sm leading-relaxed">
                      {generatedProject.project.justification.substring(0, 500)}
                      {generatedProject.project.justification.length > 500 && '...'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Painel Lateral */}
            <div className="space-y-6">
              {/* Resumo Financeiro */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-semibold text-green-900 mb-2">Resumo Financeiro</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-green-700">Orçamento Total:</span>
                    <span className="font-medium text-green-900">
                      {formatCurrency(generatedProject.project.budget_total)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-700">Prazo:</span>
                    <span className="font-medium text-green-900">
                      {generatedProject.project.timeline_months} meses
                    </span>
                  </div>
                </div>
              </div>

              {/* Equipe */}
              {generatedProject.project.team_members && generatedProject.project.team_members.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-semibold text-blue-900 mb-2">Equipe Técnica</h4>
                  <ul className="text-sm text-blue-800 space-y-1">
                    {generatedProject.project.team_members.slice(0, 4).map((member: any, index: number) => (
                      <li key={index}>• {member.role}</li>
                    ))}
                    {generatedProject.project.team_members.length > 4 && (
                      <li className="italic">... e mais {generatedProject.project.team_members.length - 4} profissionais</li>
                    )}
                  </ul>
                </div>
              )}

              {/* Tempo de Geração */}
              {generatedProject.generation_time && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Estatísticas</h4>
                  <div className="text-sm text-gray-600">
                    <p>Gerado em: {generatedProject.generation_time.toFixed(2)}s</p>
                    <p>Modelo: GPT-4 Turbo especializado</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Recomendações */}
          {generatedProject.recommendations && generatedProject.recommendations.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-3">Recomendações da IA</h4>
              <ul className="list-disc list-inside text-gray-700 space-y-2">
                {generatedProject.recommendations.map((recommendation: string, index: number) => (
                  <li key={index}>{recommendation}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Botões de Ação */}
          <div className="mt-6 pt-6 border-t border-gray-200 flex justify-end space-x-4">
            <button
              type="button"
              className="btn-outline"
              onClick={() => {
                // Implementar download do projeto em PDF
                console.log('Download PDF do projeto');
              }}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Download PDF
            </button>
            
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                // Implementar criação do projeto no sistema
                console.log('Criar projeto no sistema');
              }}
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Criar Projeto no Sistema
            </button>
          </div>
        </div>
      )}
    </div>
  );
}