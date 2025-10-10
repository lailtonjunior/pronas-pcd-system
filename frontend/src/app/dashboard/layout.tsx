// Arquivo: frontend/src/app/dashboard/layout.tsx
"use client";

import { useAuth } from "@/hooks/useAuth";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, ReactNode } from "react";

const Sidebar = () => {
    const { logout } = useAuth();
    return (
        <div className="w-64 bg-white border-r">
            <div className="p-4">
                <h1 className="text-xl font-bold">PRONAS/PCD</h1>
            </div>
            <nav className="mt-6">
                <Link href="/dashboard/projects" className="block px-4 py-2 text-gray-600 hover:bg-gray-100">
                    Projetos
                </Link>
                <Link href="/dashboard/institutions" className="block px-4 py-2 text-gray-600 hover:bg-gray-100">
                    Instituições
                </Link>
                {/* Adicionar mais links aqui */}
            </nav>
            <div className="absolute bottom-0 w-full p-4">
                <button onClick={logout} className="w-full text-left px-4 py-2 text-gray-600 hover:bg-gray-100">
                    Sair
                </button>
            </div>
        </div>
    );
};

export default function DashboardLayout({ children }: { children: ReactNode }) {
    const { isAuthenticated, loading } = useAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, loading, router]);

    if (loading) {
        return <div>Carregando...</div>; // Ou um componente de loading melhor
    }

    if (!isAuthenticated) {
        return null; // ou redireciona
    }

    return (
        <div className="flex h-screen">
            <Sidebar />
            <main className="flex-1 p-8 overflow-y-auto">
                {children}
            </main>
        </div>
    );
}