// Arquivo: frontend/src/app/layout.tsx

import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/contexts/AuthContext';
import { Toaster } from 'react-hot-toast'; // Para exibir notificações

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Sistema PRONAS/PCD',
  description: 'Sistema de Gestão para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <AuthProvider>
          {children}
          <Toaster position="top-right" />
        </AuthProvider>
      </body>
    </html>
  );
}