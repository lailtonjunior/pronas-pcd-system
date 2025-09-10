/**
 * Formulário completo para cadastro de instituições PRONAS/PCD
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useForm, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { InstitutionFormData, InstitutionType, ApiResponse } from '@/types/pronas';
import { useApi } from '@/lib/api';

// Schema de validação baseado nas regras PRONAS/PCD
const institutionSchema = z.object({
  cnpj: z.string()
    .min(18, 'CNPJ deve ter 18 caracteres')
    .regex(/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/, 'CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX'),
  name: z.string()
    .min(3, 'Nome deve ter pelo menos 3 caracteres')
    .max(255, 'Nome deve ter no máximo 255 caracteres'),
  legal_name: z.string()
    .min(3, 'Razão social deve ter pelo menos 3 caracteres')
    .max(255, 'Razão social deve ter no máximo 255 caracteres'),
  institution_type: z.nativeEnum(InstitutionType, {
    errorMap: () => ({ message: 'Selecione um tipo de instituição válido' }),
  }),
  cep: z.string()
    .min(9, 'CEP deve ter 9 caracteres')
    .regex(/^\d{5}-\d{3}$/, 'CEP deve estar no formato XXXXX-XXX'),
  address: z.string()
    .min(10, 'Endereço deve ter pelo menos 10 caracteres')
    .max(500, 'Endereço deve ter no máximo 500 caracteres'),
  city: z.string()
    .min(2, 'Cidade deve ter pelo menos 2 caracteres')
    .max(100, 'Cidade deve ter no máximo 100 caracteres'),
  state: z.string()
    .min(2, 'Estado deve ter 2 caracteres')
    .max(2, 'Estado deve ter 2 caracteres')
    .regex(/^[A-Z]{2}$/, 'Estado deve ser uma UF válida (ex: SP, RJ)'),
  phone: z.string()
    .regex(/^\(\d{2}\) \d{4,5}-\d{4}$/, 'Telefone deve estar no formato (XX) XXXXX-XXXX')
    .optional()
    .or(z.literal('')),
  email: z.string()
    .email('Email deve ser válido')
    .max(255, 'Email deve ter no máximo 255 caracteres'),
  website: z.string()
    .url('Website deve ser uma URL válida')
    .optional()
    .or(z.literal('')),
  legal_representative: z.string()
    .min(3, 'Nome do representante deve ter pelo menos 3 caracteres')
    .max(255, 'Nome do representante deve ter no máximo 255 caracteres'),
  legal_representative_cpf: z.string()
    .regex(/^\d{3}\.\d{3}\.\d{3}-\d{2}$/, 'CPF deve estar no formato XXX.XXX.XXX-XX')
    .optional()
    .or(z.literal('')),
  technical_responsible: z.string()
    .max(255, 'Nome do responsável técnico deve ter no máximo 255 caracteres')
    .optional()
    .or(z.literal('')),
  technical_responsible_registration: z.string()
    .max(50, 'Registro profissional deve ter no máximo 50 caracteres')
    .optional()
    .or(z.literal('')),
  experience_proof: z.string()
    .min(50, 'Comprovação de experiência deve ter pelo menos 50 caracteres')
    .optional()
    .or(z.literal('')),
  services_offered: z.string().optional().or(z.literal('')),
  technical_capacity: z.string().optional().or(z.literal('')),
  partnership_history: z.string().optional().or(z.literal('')),
});

type InstitutionFormValues = z.infer<typeof institutionSchema>;

interface InstitutionFormProps {
  initialData?: Partial<InstitutionFormData>;
  onSubmit?: (data: InstitutionFormData) => void;
  onCancel?: () => void;
  isLoading?: boolean;
  mode?: 'create' | 'edit';
}

export default function InstitutionForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
  mode = 'create'
}: InstitutionFormProps) {
  const api = useApi();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    trigger
  } = useForm<InstitutionFormValues>({
    resolver: zodResolver(institutionSchema),
    defaultValues: initialData,
  });

  // Estados brasileiros
  const brasileirOStates = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA',
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN',
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
  ];

  // Tipos de instituição com labels em português
  const institutionTypeLabels = {
    [InstitutionType.HOSPITAL]: 'Hospital',
    [InstitutionType.APAE]: 'APAE - Associação de Pais e Amigos dos Excepcionais',
    [InstitutionType.ONG]: 'ONG - Organização Não Governamental',
    [InstitutionType.FUNDACAO]: 'Fundação',
    [InstitutionType.ASSOCIACAO]: 'Associação',
    [InstitutionType.INSTITUTO]: 'Instituto',
    [InstitutionType.COOPERATIVA]: 'Cooperativa',
    [InstitutionType.OSCIP]: 'OSCIP - Organização da Sociedade Civil de Interesse Público',
  };

  // Buscar CEP automaticamente
  const watchedCep = watch('cep');
  useEffect(() => {
    const fetchCepData = async (cep: string) => {
      if (cep && cep.length === 9) {
        try {
          const cleanCep = cep.replace('-', '');
          const response = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
          const data = await response.json();
          
          if (!data.erro) {
            setValue('address', data.logradouro || '');
            setValue('city', data.localidade || '');
            setValue('state', data.uf || '');
            
            // Revalidar campos preenchidos
            trigger(['address', 'city', 'state']);
          }
        } catch (error) {
          console.error('Erro ao buscar CEP:', error);
        }
      }
    };

    const timeoutId = setTimeout(() => {
      if (watchedCep) {
        fetchCepData(watchedCep);
      }
    }, 500); // Debounce de 500ms

    return () => clearTimeout(timeoutId);
  }, [watchedCep, setValue, trigger]);

  const handleFormSubmit: SubmitHandler<InstitutionFormValues> = async (data) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      if (onSubmit) {
        await onSubmit(data);
      } else {
        // Submit padrão via API
        if (mode === 'create') {
          await api.createInstitution(data);
        } else {
          // Para edição, seria necessário o ID
          console.warn('Modo de edição requer ID da instituição');
        }
      }
      
      setSubmitSuccess(true);
    } catch (error) {
      setSubmitError(
        error instanceof Error ? error.message : 'Erro ao salvar instituição'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  // Máscaras para campos
  const formatCnpj = (value: string) => {
    return value
      .replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '$1.$2')
      .replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/\.(\d{3})(\d)/, '.$1/$2')
      .replace(/(\d{4})(\d)/, '$1-$2')
      .substring(0, 18);
  };

  const formatCep = (value: string) => {
    return value
      .replace(/\D/g, '')
      .replace(/^(\d{5})(\d)/, '$1-$2')
      .substring(0, 9);
  };

  const formatPhone = (value: string) => {
    return value
      .replace(/\D/g, '')
      .replace(/^(\d{2})(\d)/, '($1) $2')
      .replace(/(\d{4,5})(\d{4})$/, '$1-$2')
      .substring(0, 15);
  };

  const formatCpf = (value: string) => {
    return value
      .replace(/\D/g, '')
      .replace(/^(\d{3})(\d)/, '$1.$2')
      .replace(/^(\d{3})\.(\d{3})(\d)/, '$1.$2.$3')
      .replace(/\.(\d{3})(\d)/, '.$1-$2')
      .substring(0, 14);
  };

  return (
    <div className="card max-w-4xl mx-auto">
      <div className="card-header">
        <h2 className="card-title">
          {mode === 'create' ? 'Cadastrar Nova Instituição' : 'Editar Instituição'}
        </h2>
        <p className="card-subtitle">
          Preencha todas as informações necessárias para o credenciamento PRONAS/PCD
        </p>
      </div>

      {submitSuccess && (
        <div className="alert alert-success">
          <strong>Sucesso!</strong> Instituição {mode === 'create' ? 'cadastrada' : 'atualizada'} com sucesso.
        </div>
      )}

      {submitError && (
        <div className="alert alert-danger">
          <strong>Erro!</strong> {submitError}
        </div>
      )}

      <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
        {/* Informações Básicas */}
        <fieldset className="border border-gray-200 rounded-lg p-4">
          <legend className="text-lg font-semibold text-gray-900 px-2">Informações Básicas</legend>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* CNPJ */}
            <div className="form-group">
              <label htmlFor="cnpj" className="form-label">
                CNPJ <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="cnpj"
                {...register('cnpj')}
                onChange={(e) => {
                  const formatted = formatCnpj(e.target.value);
                  setValue('cnpj', formatted);
                }}
                className={`form-input ${errors.cnpj ? 'border-red-500' : ''}`}
                placeholder="XX.XXX.XXX/XXXX-XX"
                maxLength={18}
              />
              {errors.cnpj && <p className="form-error">{errors.cnpj.message}</p>}
            </div>

            {/* Tipo de Instituição */}
            <div className="form-group">
              <label htmlFor="institution_type" className="form-label">
                Tipo de Instituição <span className="text-red-500">*</span>
              </label>
              <select
                id="institution_type"
                {...register('institution_type')}
                className={`form-select ${errors.institution_type ? 'border-red-500' : ''}`}
              >
                <option value="">Selecione o tipo</option>
                {Object.entries(institutionTypeLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
              {errors.institution_type && <p className="form-error">{errors.institution_type.message}</p>}
            </div>

            {/* Nome Fantasia */}
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                Nome Fantasia <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="name"
                {...register('name')}
                className={`form-input ${errors.name ? 'border-red-500' : ''}`}
                placeholder="Nome da instituição"
                maxLength={255}
              />
              {errors.name && <p className="form-error">{errors.name.message}</p>}
            </div>

            {/* Razão Social */}
            <div className="form-group">
              <label htmlFor="legal_name" className="form-label">
                Razão Social <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="legal_name"
                {...register('legal_name')}
                className={`form-input ${errors.legal_name ? 'border-red-500' : ''}`}
                placeholder="Razão social da instituição"
                maxLength={255}
              />
              {errors.legal_name && <p className="form-error">{errors.legal_name.message}</p>}
            </div>
          </div>
        </fieldset>

        {/* Endereço */}
        <fieldset className="border border-gray-200 rounded-lg p-4">
          <legend className="text-lg font-semibold text-gray-900 px-2">Endereço</legend>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* CEP */}
            <div className="form-group">
              <label htmlFor="cep" className="form-label">
                CEP <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="cep"
                {...register('cep')}
                onChange={(e) => {
                  const formatted = formatCep(e.target.value);
                  setValue('cep', formatted);
                }}
                className={`form-input ${errors.cep ? 'border-red-500' : ''}`}
                placeholder="XXXXX-XXX"
                maxLength={9}
              />
              {errors.cep && <p className="form-error">{errors.cep.message}</p>}
              <p className="form-help">O endereço será preenchido automaticamente</p>
            </div>

            {/* Cidade */}
            <div className="form-group">
              <label htmlFor="city" className="form-label">
                Cidade <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="city"
                {...register('city')}
                className={`form-input ${errors.city ? 'border-red-500' : ''}`}
                placeholder="Cidade"
                maxLength={100}
              />
              {errors.city && <p className="form-error">{errors.city.message}</p>}
            </div>

            {/* Estado */}
            <div className="form-group">
              <label htmlFor="state" className="form-label">
                Estado <span className="text-red-500">*</span>
              </label>
              <select
                id="state"
                {...register('state')}
                className={`form-select ${errors.state ? 'border-red-500' : ''}`}
              >
                <option value="">Selecione</option>
                {brasileirOStates.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
              {errors.state && <p className="form-error">{errors.state.message}</p>}
            </div>

            {/* Endereço Completo */}
            <div className="form-group md:col-span-3">
              <label htmlFor="address" className="form-label">
                Endereço Completo <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="address"
                {...register('address')}
                className={`form-input ${errors.address ? 'border-red-500' : ''}`}
                placeholder="Rua, número, complemento"
                maxLength={500}
              />
              {errors.address && <p className="form-error">{errors.address.message}</p>}
            </div>
          </div>
        </fieldset>

        {/* Contato */}
        <fieldset className="border border-gray-200 rounded-lg p-4">
          <legend className="text-lg font-semibold text-gray-900 px-2">Informações de Contato</legend>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Email */}
            <div className="form-group">
              <label htmlFor="email" className="form-label">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="email"
                {...register('email')}
                className={`form-input ${errors.email ? 'border-red-500' : ''}`}
                placeholder="contato@instituicao.org.br"
                maxLength={255}
              />
              {errors.email && <p className="form-error">{errors.email.message}</p>}
            </div>

            {/* Telefone */}
            <div className="form-group">
              <label htmlFor="phone" className="form-label">
                Telefone
              </label>
              <input
                type="text"
                id="phone"
                {...register('phone')}
                onChange={(e) => {
                  const formatted = formatPhone(e.target.value);
                  setValue('phone', formatted);
                }}
                className={`form-input ${errors.phone ? 'border-red-500' : ''}`}
                placeholder="(XX) XXXXX-XXXX"
                maxLength={15}
              />
              {errors.phone && <p className="form-error">{errors.phone.message}</p>}
            </div>

            {/* Website */}
            <div className="form-group md:col-span-2">
              <label htmlFor="website" className="form-label">
                Website
              </label>
              <input
                type="url"
                id="website"
                {...register('website')}
                className={`form-input ${errors.website ? 'border-red-500' : ''}`}
                placeholder="https://www.instituicao.org.br"
                maxLength={255}
              />
              {errors.website && <p className="form-error">{errors.website.message}</p>}
            </div>
          </div>
        </fieldset>

        {/* Responsáveis */}
        <fieldset className="border border-gray-200 rounded-lg p-4">
          <legend className="text-lg font-semibold text-gray-900 px-2">Responsáveis</legend>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Representante Legal */}
            <div className="form-group">
              <label htmlFor="legal_representative" className="form-label">
                Representante Legal <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="legal_representative"
                {...register('legal_representative')}
                className={`form-input ${errors.legal_representative ? 'border-red-500' : ''}`}
                placeholder="Nome completo"
                maxLength={255}
              />
              {errors.legal_representative && <p className="form-error">{errors.legal_representative.message}</p>}
            </div>

            {/* CPF do Representante */}
            <div className="form-group">
              <label htmlFor="legal_representative_cpf" className="form-label">
                CPF do Representante Legal
              </label>
              <input
                type="text"
                id="legal_representative_cpf"
                {...register('legal_representative_cpf')}
                onChange={(e) => {
                  const formatted = formatCpf(e.target.value);
                  setValue('legal_representative_cpf', formatted);
                }}
                className={`form-input ${errors.legal_representative_cpf ? 'border-red-500' : ''}`}
                placeholder="XXX.XXX.XXX-XX"
                maxLength={14}
              />
              {errors.legal_representative_cpf && <p className="form-error">{errors.legal_representative_cpf.message}</p>}
            </div>

            {/* Responsável Técnico */}
            <div className="form-group">
              <label htmlFor="technical_responsible" className="form-label">
                Responsável Técnico
              </label>
              <input
                type="text"
                id="technical_responsible"
                {...register('technical_responsible')}
                className={`form-input ${errors.technical_responsible ? 'border-red-500' : ''}`}
                placeholder="Nome completo"
                maxLength={255}
              />
              {errors.technical_responsible && <p className="form-error">{errors.technical_responsible.message}</p>}
            </div>

            {/* Registro Profissional */}
            <div className="form-group">
              <label htmlFor="technical_responsible_registration" className="form-label">
                Registro Profissional
              </label>
              <input
                type="text"
                id="technical_responsible_registration"
                {...register('technical_responsible_registration')}
                className={`form-input ${errors.technical_responsible_registration ? 'border-red-500' : ''}`}
                placeholder="CRM, CRF, CREFITO, etc."
                maxLength={50}
              />
              {errors.technical_responsible_registration && <p className="form-error">{errors.technical_responsible_registration.message}</p>}
              <p className="form-help">Ex: CRM/SP 123456, CREFITO/RJ 54321</p>
            </div>
          </div>
        </fieldset>

        {/* Informações Complementares */}
        <fieldset className="border border-gray-200 rounded-lg p-4">
          <legend className="text-lg font-semibold text-gray-900 px-2">Informações Complementares</legend>
          
          <div className="space-y-4">
            {/* Comprovação de Experiência */}
            <div className="form-group">
              <label htmlFor="experience_proof" className="form-label">
                Comprovação de Experiência
              </label>
              <textarea
                id="experience_proof"
                {...register('experience_proof')}
                className={`form-textarea ${errors.experience_proof ? 'border-red-500' : ''}`}
                rows={4}
                placeholder="Descreva a experiência da instituição no atendimento à pessoa com deficiência (mínimo 50 caracteres)"
              />
              {errors.experience_proof && <p className="form-error">{errors.experience_proof.message}</p>}
              <p className="form-help">Informações sobre histórico de atendimento, projetos realizados, etc.</p>
            </div>

            {/* Serviços Oferecidos */}
            <div className="form-group">
              <label htmlFor="services_offered" className="form-label">
                Serviços Oferecidos
              </label>
              <textarea
                id="services_offered"
                {...register('services_offered')}
                className="form-textarea"
                rows={3}
                placeholder="Descreva os serviços atualmente oferecidos pela instituição"
              />
            </div>

            {/* Capacidade Técnica */}
            <div className="form-group">
              <label htmlFor="technical_capacity" className="form-label">
                Capacidade Técnica
              </label>
              <textarea
                id="technical_capacity"
                {...register('technical_capacity')}
                className="form-textarea"
                rows={3}
                placeholder="Descreva a equipe técnica e infraestrutura disponível"
              />
            </div>

            {/* Histórico de Parcerias */}
            <div className="form-group">
              <label htmlFor="partnership_history" className="form-label">
                Histórico de Parcerias
              </label>
              <textarea
                id="partnership_history"
                {...register('partnership_history')}
                className="form-textarea"
                rows={3}
                placeholder="Informe parcerias anteriores com órgãos públicos ou privados"
              />
            </div>
          </div>
        </fieldset>

        {/* Botões */}
        <div className="flex justify-end space-x-4 pt-6 border-t border-gray-200">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="btn-outline"
              disabled={isSubmitting}
            >
              Cancelar
            </button>
          )}
          
          <button
            type="submit"
            className="btn-primary"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting ? (
              <>
                <div className="spinner mr-2"></div>
                {mode === 'create' ? 'Cadastrando...' : 'Salvando...'}
              </>
            ) : (
              mode === 'create' ? 'Cadastrar Instituição' : 'Salvar Alterações'
            )}
          </button>
        </div>
      </form>
    </div>
  );
}