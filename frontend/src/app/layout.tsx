/**
 * Layout principal da aplicação PRONAS/PCD
 */

import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Sistema PRONAS/PCD',
  description: 'Sistema de Gestão para o Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência',
  keywords: 'PRONAS, PCD, pessoa com deficiência, saúde, ministério da saúde',
  authors: [{ name: 'Sistema PRONAS/PCD' }],
  creator: 'Sistema PRONAS/PCD',
  publisher: 'Ministério da Saúde',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-gray-50 text-gray-900 antialiased`}>
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}