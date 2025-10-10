// Arquivo: frontend/src/app/dashboard/institutions/new/page.tsx
"use client";

import InstitutionForm from "@/components/forms/InstitutionForm";
import { apiClient } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";

export default function NewInstitutionPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (data: any) => {
        setIsLoading(true);
        toast.promise(
            apiClient.createInstitution(data),
            {
                loading: 'Salvando instituição...',
                success: () => {
                    router.push('/dashboard/institutions');
                    return <b>Instituição salva com sucesso!</b>;
                },
                error: <b>Não foi possível salvar a instituição.</b>,
            }
        ).finally(() => setIsLoading(false));
    };

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Nova Instituição</h1>
            <InstitutionForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
    );
}