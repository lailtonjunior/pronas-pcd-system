// Arquivo: frontend/src/components/forms/AIProjectGenerator.tsx
"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function AIProjectGenerator() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Assistente de IA PRONAS/PCD</CardTitle>
        <CardDescription>
          Use nossa IA para gerar uma estrutura inicial para o seu projeto.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="mb-4">
          Esta funcionalidade ainda está em desenvolvimento.
        </p>
        <Button disabled>Gerar com IA</Button>
      </CardContent>
    </Card>
  );
}