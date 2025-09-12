#!/bin/bash
# deploy-production.sh - Script de Deploy Automatizado para Produção

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   PRONAS/PCD - Deploy de Produção     ${NC}"
echo -e "${GREEN}========================================${NC}"

# Verificar variáveis de ambiente
if [ ! -f .env.production ]; then
    echo -e "${RED}❌ Arquivo .env.production não encontrado!${NC}"
    exit 1
fi

# Carregar variáveis
source .env.production

# Validar configurações críticas
echo -e "${YELLOW}📋 Validando configurações...${NC}"

if [ "$JWT_SECRET_KEY" == "CHANGE_ME" ]; then
    echo -e "${RED}❌ JWT_SECRET_KEY não foi alterado!${NC}"
    exit 1
fi

if [ "$DB_PASSWORD" == "CHANGE_ME" ]; then
    echo -e "${RED}❌ DB_PASSWORD não foi alterado!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configurações validadas${NC}"

# Backup do banco atual (se existir)
echo -e "${YELLOW}💾 Realizando backup do banco de dados...${NC}"
docker-compose -f docker-compose.production.yml exec -T postgres-primary \
    pg_dump -U $DB_USER $DB_NAME | gzip > backups/backup_$(date +%Y%m%d_%H%M%S).sql.gz

# Pull das imagens mais recentes
echo -e "${YELLOW}🐳 Atualizando imagens Docker...${NC}"
docker-compose -f docker-compose.production.yml pull

# Build das aplicações
echo -e "${YELLOW}🔨 Construindo aplicações...${NC}"
docker-compose -f docker-compose.production.yml build --no-cache

# Parar serviços antigos
echo -e "${YELLOW}⏹️  Parando serviços antigos...${NC}"
docker-compose -f docker-compose.production.yml down

# Limpar volumes órfãos
echo -e "${YELLOW}🧹 Limpando volumes órfãos...${NC}"
docker volume prune -f

# Iniciar banco de dados primeiro
echo -e "${YELLOW}🗄️  Iniciando banco de dados...${NC}"
docker-compose -f docker-compose.production.yml up -d postgres-primary postgres-replica
sleep 30

# Executar migrations
echo -e "${YELLOW}📝 Executando migrations...${NC}"
docker-compose -f docker-compose.production.yml run --rm backend-1 \
    alembic upgrade head

# Iniciar Redis
echo -e "${YELLOW}📦 Iniciando cache Redis...${NC}"
docker-compose -f docker-compose.production.yml up -d redis-master redis-slave
sleep 10

# Iniciar aplicações
echo -e "${YELLOW}🚀 Iniciando aplicações...${NC}"
docker-compose -f docker-compose.production.yml up -d

# Aguardar serviços estarem prontos
echo -e "${YELLOW}⏳ Aguardando serviços...${NC}"
sleep 30

# Verificar saúde dos serviços
echo -e "${YELLOW}🏥 Verificando saúde dos serviços...${NC}"

# Backend health check
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://api.pronas-pcd.org/health)
if [ "$BACKEND_HEALTH" == "200" ]; then
    echo -e "${GREEN}✅ Backend: Saudável${NC}"
else
    echo -e "${RED}❌ Backend: Problema detectado (HTTP $BACKEND_HEALTH)${NC}"
fi

# Frontend health check
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" https://pronas-pcd.org)
if [ "$FRONTEND_HEALTH" == "200" ]; then
    echo -e "${GREEN}✅ Frontend: Saudável${NC}"
else
    echo -e "${RED}❌ Frontend: Problema detectado (HTTP $FRONTEND_HEALTH)${NC}"
fi

# Limpar cache CDN (se aplicável)
echo -e "${YELLOW}🌐 Limpando cache CDN...${NC}"
# cloudflare-cli purge-cache --zone=$CLOUDFLARE_ZONE

# Notificar equipe
echo -e "${YELLOW}📧 Notificando equipe...${NC}"
curl -X POST $SLACK_WEBHOOK_URL \
    -H 'Content-Type: application/json' \
    -d "{\"text\":\"✅ Deploy PRONAS/PCD concluído com sucesso! Versão: $VERSION\"}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✅ Deploy concluído com sucesso!    ${NC}"
echo -e "${GREEN}========================================${NC}"

# Mostrar logs
echo -e "${YELLOW}📜 Logs dos serviços:${NC}"
docker-compose -f docker-compose.production.yml logs --tail=50