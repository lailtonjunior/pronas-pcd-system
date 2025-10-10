// Arquivo: frontend/src/hooks/useApi.ts
import { apiClient } from '@/lib/api';

/**
 * Hook para acessar a instância do ApiClient.
 * Facilita o uso em componentes sem precisar importar o apiClient diretamente.
 */
export const useApi = () => {
  return apiClient;
};