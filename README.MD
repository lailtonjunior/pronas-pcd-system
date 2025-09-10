# README.md - Documentação principal
# Sistema PRONAS/PCD 🏥

Sistema de Gestão para o **Programa Nacional de Apoio à Atenção da Saúde da Pessoa com Deficiência**

## 📋 Sobre o Projeto

Sistema completo para gestão de projetos PRONAS/PCD baseado nas diretrizes oficiais do Ministério da Saúde:

- **Lei nº 12.715/2012** (Lei do PRONAS/PCD)
- **Portaria de Consolidação nº 5/2017** - Anexo LXXXVI
- **Portaria nº 448/2002** (Natureza de Despesas)
- **Lei nº 13.146/2015** (Lei Brasileira de Inclusão)

### 🎯 Funcionalidades Principais

✅ **Gestão de Instituições**
- Cadastro completo conforme PRONAS/PCD
- Validação automática de CNPJ, CEP, dados
- Controle de credenciamento (junho/julho apenas)
- Upload de documentos obrigatórios

✅ **Geração Inteligente de Projetos**
- IA especializada nas 8 áreas prioritárias
- Geração automática de orçamentos conformes
- Equipes técnicas adequadas por área
- Validação automática de conformidade

✅ **8 Áreas Prioritárias Implementadas**
- **QSS** - Qualificação de serviços de saúde
- **RPD** - Reabilitação/habilitação da pessoa com deficiência
- **DDP** - Diagnóstico diferencial da pessoa com deficiência
- **EPD** - Identificação e estimulação precoce das deficiências
- **ITR** - Inserção e reinserção no trabalho
- **APE** - Apoio à saúde por meio de práticas esportivas
- **TAA** - Terapia assistida por animais
- **APC** - Apoio à saúde por produção artística e cultural

✅ **Dashboard Executivo**
- Estatísticas em tempo real
- Monitoramento de conformidade
- Relatórios de prestação de contas
- Métricas por área prioritária

## 🏗️ Arquitetura

### Backend
- **FastAPI + Python** - API REST completa
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões
- **MinIO** - Armazenamento de documentos
- **IA Especializada** - Motor próprio baseado nas regras PRONAS/PCD

### Frontend
- **Next.js 14** - Framework React moderno
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização utilitária
- **React Hook Form + Zod** - Formulários e validação

### Infraestrutura
- **Docker + Docker Compose** - Containerização
- **Nginx** - Reverse proxy e load balancer
- **Prometheus + Grafana** - Monitoramento
- **Backup automático** - PostgreSQL

## 🚀 Como Executar

### Pré-requisitos
- Docker 20.10+
- Docker Compose 2.0+
- Git

### Instalação Rápida

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/pronas-pcd-system.git
cd pronas-pcd-system

# 2. Copiar arquivo de ambiente
cp .env.example .env

# 3. Iniciar todos os serviços
docker-compose up -d

# 4. Aguardar inicialização (aproximadamente 2 minutos)
docker-compose logs -f

# 5. Acessar o sistema
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Grafana: http://localhost:3001
```

### Usuários Padrão (Desenvolvimento)

| Usuário | Senha | Permissões |
|---------|-------|------------|
| admin | password | Administrador completo |
| user | password | Usuário comum |
| gestor | password | Gestor de projetos |

**⚠️ IMPORTANTE:** Altere as senhas em produção!

## 📊 Monitoramento

### Endpoints de Saúde
- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost:3000
- **Sistema completo**: http://localhost/health

### Métricas
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
  - Usuário: admin
  - Senha: pronas_grafana_password

### Logs
```bash
# Ver todos os logs
docker-compose logs -f

# Logs específicos
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

## 🔧 Comandos Úteis

```bash
# Parar sistema
docker-compose down

# Reiniciar serviços
docker-compose restart

# Limpeza completa (remove volumes)
docker-compose down -v

# Backup manual
docker-compose exec backup ./backup.sh

# Acessar banco de dados
docker-compose exec postgres psql -U pronas_user -d pronas_pcd_db

# Ver status dos serviços
docker-compose ps
```

## 📁 Estrutura do Projeto

```
pronas-pcd-system/
├── 📂 backend/              # API FastAPI
│   ├── main.py             # Ponto de entrada
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Validação Pydantic
│   ├── auth.py             # Autenticação JWT
│   ├── crud.py             # Operações CRUD
│   └── ai/engine.py        # Motor de IA
├── 📂 frontend/             # Interface Next.js
│   ├── src/app/            # Rotas App Router
│   ├── src/components/     # Componentes React
│   └── src/types/          # Tipos TypeScript
├── 📂 infra/                # Infraestrutura
│   ├── nginx.conf          # Configuração Nginx
│   └── backup/             # Scripts de backup
├── 📂 monitoring/           # Monitoramento
│   ├── prometheus.yml      # Config Prometheus
│   └── grafana/            # Dashboards Grafana
├── docker-compose.yml      # Orquestração
└── .env                    # Variáveis ambiente
```

## 🔐 Segurança

### Produção
- [ ] Alterar todas as senhas padrão
- [ ] Configurar HTTPS/SSL
- [ ] Configurar firewall
- [ ] Configurar backup automático
- [ ] Configurar monitoramento de logs
- [ ] Revisar permissões de usuários

### Desenvolvimento
- Senhas padrão definidas
- HTTP sem SSL
- Logs detalhados habilitados
- CORS configurado para localhost

## 📖 Documentação da API

Acesse a documentação interativa em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Principais Endpoints

#### Autenticação
- `POST /auth/login` - Login no sistema
- `GET /auth/me` - Dados do usuário atual
- `POST /auth/logout` - Logout

#### Instituições
- `GET /institutions/` - Listar instituições
- `POST /institutions/` - Cadastrar instituição
- `POST /institutions/{id}/credential` - Solicitar credenciamento

#### Projetos
- `GET /projects/` - Listar projetos
- `POST /projects/` - Criar projeto
- `POST /projects/{id}/validate` - Validar projeto
- `PUT /projects/{id}/submit` - Submeter projeto

#### IA
- `POST /ai/generate-project` - Gerar projeto com IA
- `GET /ai/priority-areas` - Áreas prioritárias

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Ver arquivo [LICENSE](LICENSE).

## 📞 Suporte

- **Documentação**: [Wiki do projeto](wiki)
- **Issues**: [GitHub Issues](issues)
- **Email**: suporte@pronas-pcd.org

---

**Sistema PRONAS/PCD** - Desenvolvido com ❤️ para promover a inclusão e saúde das pessoas com deficiência.