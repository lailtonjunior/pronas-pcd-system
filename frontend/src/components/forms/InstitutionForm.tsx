// Arquivo: frontend/src/components/forms/InstitutionForm.tsx
"use client";

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button'; // Corrigido
import { Input } from '@/components/ui/input';   // Corrigido
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Institution } from '@/types';

const institutionSchema = z.object({
  name: z.string().min(3, "O nome deve ter pelo menos 3 caracteres."),
  cnpj: z.string().length(14, "O CNPJ deve ter 14 números."),
});

type InstitutionFormData = z.infer<typeof institutionSchema>;

interface InstitutionFormProps {
  institution?: Institution;
  onSubmit: (data: InstitutionFormData) => void;
  isLoading?: boolean;
}

export default function InstitutionForm({ institution, onSubmit, isLoading }: InstitutionFormProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<InstitutionFormData>({
    resolver: zodResolver(institutionSchema),
    defaultValues: {
      name: institution?.name || '',
      cnpj: institution?.cnpj || '',
    }
  });

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>{institution ? 'Editar Instituição' : 'Cadastrar Nova Instituição'}</CardTitle>
        <CardDescription>Preencha os dados abaixo.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="name">Nome da Instituição</Label>
            <Input id="name" {...register('name')} />
            {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="cnpj">CNPJ (apenas números)</Label>
            <Input id="cnpj" {...register('cnpj')} />
            {errors.cnpj && <p className="text-sm text-red-500">{errors.cnpj.message}</p>}
          </div>
          <div className="flex justify-end">
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Salvando...' : 'Salvar'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}