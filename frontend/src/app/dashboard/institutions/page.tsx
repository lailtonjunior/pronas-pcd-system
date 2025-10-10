// Arquivo: frontend/src/app/dashboard/institutions/page.tsx
"use client";

import React, { useEffect, useState } from 'react';
import DataTable from '@/components/ui/dataTable'; // Corrigido
import { Button } from '@/components/ui/button';     // Corrigido
import { apiClient } from '@/lib/api';
import { Institution } from '@/types';
import { useRouter } from 'next/navigation';

export default function InstitutionsPage() {
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    apiClient.getInstitutions()
      .then(data => {
        setInstitutions(data.items || []);
      })
      .catch(error => console.error("Erro ao buscar instituições:", error))
      .finally(() => setIsLoading(false));
  }, []);

  const columns = [
    { header: 'Nome da Instituição', accessor: 'name' as keyof Institution },
    { header: 'CNPJ', accessor: 'cnpj' as keyof Institution },
    { header: 'Status', accessor: 'status' as keyof Institution },
    { header: 'Cidade/UF', accessor: (item: Institution) => `${item.city}/${item.state}` },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Instituições</h1>
        <Button onClick={() => router.push('/dashboard/institutions/new')}>
          Nova Instituição
        </Button>
      </div>
      <DataTable<Institution>
        columns={columns}
        data={institutions}
        isLoading={isLoading}
        renderActions={(institution) => (
          <Button variant="outline" size="sm">Editar</Button>
        )}
      />
    </div>
  );
}