// Arquivo: frontend/src/components/ui/DataTable.tsx
"use client";

import React, { ReactNode } from 'react';

interface Column<T> {
  header: string;
  accessor: keyof T | ((item: T) => ReactNode);
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  isLoading?: boolean;
  renderActions?: (item: T) => ReactNode;
}

export default function DataTable<T extends { id: any }>({
  columns,
  data,
  isLoading = false,
  renderActions,
}: DataTableProps<T>) {

  if (isLoading) {
    return <div className="text-center p-8">Carregando dados...</div>;
  }

  if (!data || data.length === 0) {
    return <div className="text-center p-8 text-gray-500">Nenhum dado encontrado.</div>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col, index) => (
              <th
                key={index}
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              >
                {col.header}
              </th>
            ))}
            {renderActions && (
              <th scope="col" className="relative px-6 py-3">
                <span className="sr-only">Ações</span>
              </th>
            )}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {data.map((item) => (
            <tr key={item.id} className="hover:bg-gray-50">
              {columns.map((col, index) => (
                <td key={index} className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {typeof col.accessor === 'function'
                    ? col.accessor(item)
                    : (item[col.accessor] as ReactNode)}
                </td>
              ))}
              {renderActions && (
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end gap-2">
                    {renderActions(item)}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}