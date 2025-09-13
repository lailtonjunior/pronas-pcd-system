#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 3 - PARTE 1
# PRONAS/PCD System - Frontend Next.js 14 Base Configuration
# Execute na raiz do projeto após concluir o Lote 2

set -e

echo "🚀 LOTE 3 PARTE 1: Configuração Base Frontend Next.js"
echo "===================================================="

# Verificar se estrutura existe
if [ ! -d "frontend" ]; then
    echo "❌ Estrutura frontend não encontrada. Execute Lotes 1 e 2 primeiro."
    exit 1
fi

cd frontend

echo "📝 Configurando Next.js 14 + TypeScript..."

# package.json
cat > package.json << 'EOF'
{
  "name": "pronas-pcd-frontend",
  "version": "1.0.0",
  "description": "Sistema de Gestão PRONAS/PCD - Frontend",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "format": "prettier --write \"**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "test": "jest",
    "test:watch": "jest --watch"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "typescript": "5.3.3",
    "@types/react": "18.2.45",
    "@types/react-dom": "18.2.18",
    "tailwindcss": "3.3.6",
    "autoprefixer": "10.4.16",
    "postcss": "8.4.32",
    "@tailwindcss/forms": "0.5.7",
    "@headlessui/react": "1.7.17",
    "@heroicons/react": "2.0.18",
    "clsx": "2.0.0",
    "axios": "1.6.2",
    "react-hook-form": "7.48.2",
    "@hookform/resolvers": "3.3.2",
    "zod": "3.22.4",
    "react-query": "3.39.3",
    "zustand": "4.4.7",
    "date-fns": "2.30.0",
    "react-hot-toast": "2.4.1",
    "lucide-react": "0.294.0",
    "js-cookie": "3.0.5",
    "@types/js-cookie": "3.0.6"
  },
  "devDependencies": {
    "eslint": "8.55.0",
    "eslint-config-next": "14.0.4",
    "@typescript-eslint/eslint-plugin": "6.13.2",
    "@typescript-eslint/parser": "6.13.2",
    "prettier": "3.1.1",
    "@types/node": "20.10.4",
    "jest": "29.7.0",
    "@testing-library/react": "14.1.2"
  }
}
EOF

# tsconfig.json
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@/components/*": ["./src/components/*"],
      "@/lib/*": ["./src/lib/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF

# next.config.js
cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
  async redirects() {
    return [
      {
        source: '/',
        destination: '/dashboard',
        permanent: false,
      },
    ];
  },
  reactStrictMode: true,
  swcMinify: true,
};

module.exports = nextConfig;
EOF

# tailwind.config.js
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{ts,tsx}',
    './src/components/**/*.{ts,tsx}',
    './src/app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
EOF

# .eslintrc.json
cat > .eslintrc.json << 'EOF'
{
  "extends": ["next/core-web-vitals", "@typescript-eslint/recommended"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["@typescript-eslint"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
EOF

echo "✅ Configuração base criada!"

echo "📝 Criando estrutura CSS e Layout..."

# src/styles/globals.css
mkdir -p src/styles
cat > src/styles/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom styles */
@layer base {
  html {
    font-family: 'Inter', system-ui, sans-serif;
  }
}

/* Form styles */
.form-input {
  @apply block w-full rounded-md border-gray-300 shadow-sm focus:border-brand-500 focus:ring-brand-500 sm:text-sm;
}

.form-input-error {
  @apply border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500;
}

/* Button styles */
.btn-primary {
  @apply inline-flex items-center justify-center rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2;
}

.btn-secondary {
  @apply inline-flex items-center justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50;
}

/* Card styles */
.card {
  @apply rounded-lg bg-white p-6 shadow-sm ring-1 ring-gray-900/5;
}

/* Status badges */
.badge-success {
  @apply inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800;
}

.badge-warning {
  @apply inline-flex items-center rounded-full bg-yellow-100 px-2.5 py-0.5 text-xs font-medium text-yellow-800;
}

.badge-danger {
  @apply inline-flex items-center rounded-full bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800;
}
EOF

# src/app/layout.tsx
mkdir -p src/app
cat > src/app/layout.tsx << 'EOF'
import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import { Providers } from './providers';
import '../styles/globals.css';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'PRONAS/PCD - Sistema de Gestão',
  description: 'Sistema de Gestão de Projetos PRONAS/PCD - Ministério da Saúde',
  robots: {
    index: false,
    follow: false,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR" className={inter.variable}>
      <body className="min-h-screen bg-gray-50 font-sans antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
EOF

# src/app/providers.tsx
cat > src/app/providers.tsx << 'EOF'
'use client';

import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/lib/auth/auth-context';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 5 * 60 * 1000, // 5 minutes
            retry: (failureCount, error: any) => {
              if (error?.response?.status === 401) {
                return false;
              }
              return failureCount < 3;
            },
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </AuthProvider>
    </QueryClientProvider>
  );
}
EOF

echo "✅ Layout e CSS criados!"

cd ..

echo ""
echo "🎉 LOTE 3 PARTE 1 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Next.js 14 com App Router e TypeScript"
echo "• Tailwind CSS com sistema de cores PRONAS/PCD"
echo "• ESLint e Prettier configurados"
echo "• React Query e Context API preparados"
echo "• Layout base e CSS global"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 3 Parte 2 (Auth + API Client)"
echo "2. Execute: cd frontend && npm install"
echo ""
echo "📊 Status:"
echo "• Lote 3.1: ✅ Frontend base configurado"
echo "• Lote 3.2: ⏳ Auth + API (próximo)"
echo ""