#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 3 - PARTE 3
# PRONAS/PCD System - UI Components
# Execute após aplicar as Partes 1 e 2

set -e

echo "🚀 LOTE 3 PARTE 3: Componentes UI"
echo "================================="

if [ ! -d "frontend/src/lib/auth" ]; then
    echo "❌ Execute as Partes 1 e 2 primeiro."
    exit 1
fi

cd frontend

echo "📝 Criando componentes base..."

# Button component
mkdir -p src/components/ui
cat > src/components/ui/button.tsx << 'EOF'
import React from 'react';
import { cn } from '@/lib/utils';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, icon, children, disabled, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
    
    const variants = {
      primary: 'bg-brand-600 text-white hover:bg-brand-700 focus:ring-brand-500',
      secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
      danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
      outline: 'border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-brand-500',
    };

    const sizes = {
      sm: 'h-8 px-3 text-sm',
      md: 'h-10 px-4 text-sm',
      lg: 'h-12 px-6 text-base',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {icon && !loading && <span className="mr-2">{icon}</span>}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button };
EOF

# Input component
cat > src/components/ui/input.tsx << 'EOF'
import React from 'react';
import { cn } from '@/lib/utils';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type = 'text', label, error, helperText, leftIcon, rightIcon, ...props }, ref) => {
    const inputClasses = cn(
      'block w-full rounded-md border-gray-300 shadow-sm transition-colors',
      'focus:border-brand-500 focus:ring-brand-500',
      'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
      {
        'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500': error,
        'pl-10': leftIcon,
        'pr-10': rightIcon,
      },
      className
    );

    return (
      <div className="space-y-1">
        {label && (
          <label className="block text-sm font-medium text-gray-700">
            {label}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400 text-sm">{leftIcon}</span>
            </div>
          )}
          <input
            type={type}
            className={inputClasses}
            ref={ref}
            {...props}
          />
          {rightIcon && (
            <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
              <span className="text-gray-400 text-sm">{rightIcon}</span>
            </div>
          )}
        </div>
        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
        {helperText && !error && (
          <p className="text-sm text-gray-500">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
EOF

# Card component
cat > src/components/ui/card.tsx << 'EOF'
import React from 'react';
import { cn } from '@/lib/utils';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  padding?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, padding = true, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-lg bg-white shadow-sm ring-1 ring-gray-900/5',
        padding && 'p-6',
        className
      )}
      {...props}
    />
  )
);

Card.displayName = 'Card';

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('flex flex-col space-y-1.5 p-6', className)}
      {...props}
    />
  )
);

CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn('text-lg font-semibold leading-none tracking-tight', className)}
      {...props}
    />
  )
);

CardTitle.displayName = 'CardTitle';

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
  )
);

CardContent.displayName = 'CardContent';

export { Card, CardHeader, CardTitle, CardContent };
EOF

# Loading component
cat > src/components/ui/loading.tsx << 'EOF'
import React from 'react';
import { cn } from '@/lib/utils';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Loading({ size = 'md', className }: LoadingProps) {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  };

  return (
    <div className={cn('animate-spin rounded-full border-2 border-gray-300 border-t-brand-600', sizes[size], className)}>
      <span className="sr-only">Loading...</span>
    </div>
  );
}

interface LoadingOverlayProps {
  message?: string;
}

export function LoadingOverlay({ message = 'Carregando...' }: LoadingOverlayProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="rounded-lg bg-white p-6 shadow-lg">
        <div className="flex items-center space-x-4">
          <Loading size="lg" />
          <p className="text-lg font-medium text-gray-900">{message}</p>
        </div>
      </div>
    </div>
  );
}
EOF

# Badge component
cat > src/components/ui/badge.tsx << 'EOF'
import React from 'react';
import { cn } from '@/lib/utils';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'success' | 'warning' | 'danger' | 'info' | 'neutral';
  size?: 'sm' | 'md';
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = 'neutral', size = 'md', ...props }, ref) => {
    const baseClasses = 'inline-flex items-center rounded-full font-medium';
    
    const variants = {
      success: 'bg-green-100 text-green-800',
      warning: 'bg-yellow-100 text-yellow-800',
      danger: 'bg-red-100 text-red-800',
      info: 'bg-blue-100 text-blue-800',
      neutral: 'bg-gray-100 text-gray-800',
    };

    const sizes = {
      sm: 'px-2 py-0.5 text-xs',
      md: 'px-2.5 py-0.5 text-sm',
    };

    return (
      <span
        ref={ref}
        className={cn(
          baseClasses,
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };
EOF

echo "✅ Componentes UI base criados!"

echo "📝 Criando componentes específicos do domínio..."

# Status Badge for projects and users
cat > src/components/ui/status-badge.tsx << 'EOF'
import React from 'react';
import { Badge } from './badge';

interface StatusBadgeProps {
  status: string;
  type?: 'user' | 'project' | 'document' | 'institution';
  className?: string;
}

export function StatusBadge({ status, type = 'user', className }: StatusBadgeProps) {
  const getVariantAndText = () => {
    switch (type) {
      case 'user':
        switch (status) {
          case 'active':
            return { variant: 'success' as const, text: 'Ativo' };
          case 'inactive':
            return { variant: 'neutral' as const, text: 'Inativo' };
          case 'pending':
            return { variant: 'warning' as const, text: 'Pendente' };
          case 'suspended':
            return { variant: 'danger' as const, text: 'Suspenso' };
          default:
            return { variant: 'neutral' as const, text: status };
        }

      case 'project':
        switch (status) {
          case 'draft':
            return { variant: 'neutral' as const, text: 'Rascunho' };
          case 'submitted':
            return { variant: 'warning' as const, text: 'Submetido' };
          case 'under_review':
            return { variant: 'info' as const, text: 'Em Análise' };
          case 'approved':
            return { variant: 'success' as const, text: 'Aprovado' };
          case 'rejected':
            return { variant: 'danger' as const, text: 'Rejeitado' };
          case 'in_execution':
            return { variant: 'info' as const, text: 'Em Execução' };
          case 'completed':
            return { variant: 'success' as const, text: 'Concluído' };
          case 'cancelled':
            return { variant: 'danger' as const, text: 'Cancelado' };
          default:
            return { variant: 'neutral' as const, text: status };
        }

      case 'document':
        switch (status) {
          case 'uploaded':
            return { variant: 'info' as const, text: 'Enviado' };
          case 'processing':
            return { variant: 'warning' as const, text: 'Processando' };
          case 'approved':
            return { variant: 'success' as const, text: 'Aprovado' };
          case 'rejected':
            return { variant: 'danger' as const, text: 'Rejeitado' };
          case 'archived':
            return { variant: 'neutral' as const, text: 'Arquivado' };
          default:
            return { variant: 'neutral' as const, text: status };
        }

      default:
        return { variant: 'neutral' as const, text: status };
    }
  };

  const { variant, text } = getVariantAndText();

  return (
    <Badge variant={variant} className={className}>
      {text}
    </Badge>
  );
}
EOF

# Role Badge
cat > src/components/ui/role-badge.tsx << 'EOF'
import React from 'react';
import { Badge } from './badge';

interface RoleBadgeProps {
  role: 'admin' | 'gestor' | 'auditor' | 'operador';
  className?: string;
}

export function RoleBadge({ role, className }: RoleBadgeProps) {
  const getRoleInfo = () => {
    switch (role) {
      case 'admin':
        return { variant: 'danger' as const, text: 'Administrador' };
      case 'gestor':
        return { variant: 'info' as const, text: 'Gestor' };
      case 'auditor':
        return { variant: 'warning' as const, text: 'Auditor' };
      case 'operador':
        return { variant: 'neutral' as const, text: 'Operador' };
    }
  };

  const { variant, text } = getRoleInfo();

  return (
    <Badge variant={variant} className={className}>
      {text}
    </Badge>
  );
}
EOF

echo "✅ Componentes específicos criados!"

echo "📝 Criando componentes de layout..."

# Header component
mkdir -p src/components/layout
cat > src/components/layout/header.tsx << 'EOF'
'use client';

import React from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { Button } from '@/components/ui/button';
import { RoleBadge } from '@/components/ui/role-badge';

export function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return null;
  }

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">
              Sistema PRONAS/PCD
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {user.full_name}
                </p>
                <div className="flex items-center space-x-2">
                  <p className="text-xs text-gray-500">{user.email}</p>
                  <RoleBadge role={user.role} />
                </div>
              </div>
              
              <div className="w-8 h-8 bg-brand-600 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-white">
                  {user.full_name.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>

            <Button variant="secondary" onClick={logout} size="sm">
              Sair
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}
EOF

# Sidebar navigation
cat > src/components/layout/sidebar.tsx << 'EOF'
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth/auth-context';
import { cn } from '@/lib/utils';

interface NavItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  roles?: ('admin' | 'gestor' | 'auditor' | 'operador')[];
}

const navigation: NavItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 5a2 2 0 012-2h4a2 2 0 012 2v14l-5-3-5 3V5z" />
      </svg>
    ),
  },
  {
    name: 'Usuários',
    href: '/users',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
      </svg>
    ),
    roles: ['admin', 'gestor'],
  },
  {
    name: 'Instituições',
    href: '/institutions',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
      </svg>
    ),
    roles: ['admin', 'auditor'],
  },
  {
    name: 'Projetos',
    href: '/projects',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
  },
  {
    name: 'Documentos',
    href: '/documents',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    name: 'Auditoria',
    href: '/audit',
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    roles: ['admin', 'auditor'],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  if (!user) return null;

  const filteredNavigation = navigation.filter(item => 
    !item.roles || item.roles.includes(user.role)
  );

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="bg-gray-800 flex flex-col flex-grow pt-5 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <h1 className="text-white text-lg font-semibold">PRONAS/PCD</h1>
        </div>
        <div className="mt-5 flex-1 flex flex-col">
          <nav className="flex-1 px-2 pb-4 space-y-1">
            {filteredNavigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  )}
                >
                  <span className="mr-3 flex-shrink-0">
                    {item.icon}
                  </span>
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </div>
  );
}
EOF

# Main layout wrapper
cat > src/components/layout/layout.tsx << 'EOF'
'use client';

import React from 'react';
import { useAuth } from '@/lib/auth/auth-context';
import { Header } from './header';
import { Sidebar } from './sidebar';
import { Loading } from '@/components/ui/loading';

interface LayoutProps {
  children: React.ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div className="h-screen bg-gray-50 flex overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden md:pl-64">
        <Header />
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
EOF

echo "✅ Componentes de layout criados!"

cd ..

echo ""
echo "🎉 LOTE 3 PARTE 3 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Componentes UI base (Button, Input, Card, Loading, Badge)"
echo "• Componentes específicos (StatusBadge, RoleBadge)"
echo "• Sistema de layout completo (Header, Sidebar, Layout)"
echo "• Navegação com controle de permissões por role"
echo "• Design system consistente com Tailwind CSS"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 3 Parte 4 (Pages principais - Login, Dashboard)"
echo "2. Execute: cd frontend && npm install"
echo ""
echo "📊 Status:"
echo "• Lote 3.1: ✅ Frontend base"
echo "• Lote 3.2: ✅ Auth + API Client"
echo "• Lote 3.3: ✅ UI Components"
echo "• Lote 3.4: ⏳ Pages principais (próximo)"
echo ""