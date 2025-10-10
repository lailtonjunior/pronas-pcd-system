// Arquivo: frontend/src/app/dashboard/projects/page.tsx
"use client";

import React, { useEffect, useState } from 'react';
import DataTable from '@/components/ui/DataTable';
import { Button } from '@/components/ui/button';
import { apiClient } from '@/lib/api';
import { Project } from '@/types';
import { format } from 'date-fns';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    apiClient.getProjects()
      .then(data => {
        setProjects(data.items || []);
      })
      .catch(error => console.error("Erro ao buscar projetos:", error))
      .finally(() => setIsLoading(false));
  }, []);

  const columns = [
    {
      header: 'Título',
      accessor: 'title' as keyof Project,
    },
    {
      header: 'Status',
      accessor: 'status' as keyof Project,
    },
    {
      header: 'Orçamento Total',
      accessor: (item: Project) => `R$ ${item.total_budget.toLocaleString('pt-BR')}`,
    },
    {
        header: 'Data de Início',
        accessor: (item: Project) => format(new Date(item.start_date), 'dd/MM/yyyy'),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Meus Projetos</h1>
        <Button>Novo Projeto</Button>
      </div>

      <DataTable<Project>
        columns={columns}
        data={projects}
        isLoading={isLoading}
        renderActions={(project) => (
          <>
            <Button variant="outline" size="sm">Editar</Button>
            <Button variant="destructive" size="sm">Excluir</Button>
          </>
        )}
      />
    </div>
  );
}