// Arquivo: frontend/src/lib/auth.ts

const TOKEN_KEY = 'pronas_access_token';

/**
 * Salva o token de acesso no localStorage.
 * @param token O token JWT a ser salvo.
 */
export const saveToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
};

/**
 * Recupera o token de acesso do localStorage.
 * @returns O token JWT ou null se não for encontrado.
 */
export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
};

/**
 * Remove o token de acesso do localStorage.
 */
export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
};