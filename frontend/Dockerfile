# Estágio 1: Builder - Constrói a aplicação Next.js
FROM node:18-alpine AS builder
WORKDIR /app

# Copia os manifestos de pacotes e instala dependências (melhora o cache)
COPY package.json package-lock.json* ./
RUN npm ci

# Copia TODO o código-fonte, incluindo a pasta /public
# ESTA É A LINHA CRÍTICA QUE CORRIGE O ERRO
COPY . .

# Constrói a aplicação para produção
RUN npm run build

# Estágio 2: Runner - Executa a aplicação otimizada
FROM node:18-alpine AS runner
WORKDIR /app

# Cria um usuário e grupo não-root para segurança
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Define o ambiente para produção
ENV NODE_ENV=production

# Copia os artefatos da build do estágio anterior
# Esta linha agora funcionará, pois /app/public existe no builder
COPY --from=builder /app/public ./public

# Copia os arquivos da aplicação standalone
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Define o usuário não-root para executar a aplicação
USER nextjs

EXPOSE 3000

ENV PORT 3000

# Comando para iniciar o servidor Next.js
CMD ["node", "server.js"]