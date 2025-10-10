// Arquivo: frontend/src/lib/validators.ts
import * as z from 'zod';

export const loginSchema = z.object({
  email: z.string().email({ message: "Por favor, insira um email válido." }),
  password: z.string().min(6, { message: "A senha deve ter pelo menos 6 caracteres." }),
});

// Podemos adicionar outros schemas aqui no futuro