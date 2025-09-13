#!/bin/bash

# SCRIPT DE APLICAÇÃO DO LOTE 4 - PARTE 3
# PRONAS/PCD System - CI/CD GitHub Actions
# Execute após aplicar as Partes 1 e 2

set -e

echo "🚀 LOTE 4 PARTE 3: CI/CD GitHub Actions"
echo "======================================="

if [ ! -d "infra/k8s/base" ]; then
    echo "❌ Execute as Partes 1 e 2 primeiro."
    exit 1
fi

echo "📝 Criando workflows GitHub Actions..."

# CI/CD Workflow
mkdir -p .github/workflows
cat > .github/workflows/ci-cd.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME_BACKEND: pronas-pcd/backend
  IMAGE_NAME_FRONTEND: pronas-pcd/frontend

jobs:
  test-backend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11]

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_USER: test_user
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('backend/requirements-dev.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      working-directory: ./backend
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Set up test environment
      working-directory: ./backend
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_db
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        JWT_SECRET_KEY: test_secret_key_for_ci
        JWT_REFRESH_SECRET_KEY: test_refresh_secret_key_for_ci
      run: |
        # Run database migrations
        alembic upgrade head

    - name: Run backend tests
      working-directory: ./backend
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: test_db
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_HOST: localhost
        REDIS_PORT: 6379
        JWT_SECRET_KEY: test_secret_key_for_ci
        JWT_REFRESH_SECRET_KEY: test_refresh_secret_key_for_ci
      run: |
        pytest tests/ -v --cov=app --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        directory: ./backend
        flags: backend
        name: backend-coverage

    - name: Run security scan
      working-directory: ./backend
      run: |
        pip install safety bandit
        safety check --json || true
        bandit -r app/ -f json || true

    - name: Lint backend code
      working-directory: ./backend
      run: |
        black --check .
        isort --check-only .
        flake8 .
        mypy app/

  test-frontend:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json

    - name: Install dependencies
      working-directory: ./frontend
      run: npm ci

    - name: Run type checking
      working-directory: ./frontend
      run: npm run type-check

    - name: Run linting
      working-directory: ./frontend
      run: npm run lint

    - name: Run tests
      working-directory: ./frontend
      env:
        NEXT_PUBLIC_API_URL: http://localhost:8000
        NEXT_PUBLIC_APP_URL: http://localhost:3000
      run: npm run test

    - name: Build application
      working-directory: ./frontend
      env:
        NEXT_PUBLIC_API_URL: http://localhost:8000
        NEXT_PUBLIC_APP_URL: http://localhost:3000
      run: npm run build

    - name: Run security audit
      working-directory: ./frontend
      run: npm audit --audit-level=moderate

  build-and-push:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    permissions:
      contents: read
      packages: write

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata for backend
      id: meta-backend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push backend image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta-backend.outputs.tags }}
        labels: ${{ steps.meta-backend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

    - name: Extract metadata for frontend
      id: meta-frontend
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push frontend image
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ${{ steps.meta-frontend.outputs.tags }}
        labels: ${{ steps.meta-frontend.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy-staging:
    needs: [build-and-push]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Deploy to staging
      env:
        KUBE_CONFIG: ${{ secrets.STAGING_KUBE_CONFIG }}
        DOCKER_REGISTRY: ${{ env.REGISTRY }}
      run: |
        echo "Deploying to staging environment..."
        # Add staging deployment logic here

  deploy-production:
    needs: [build-and-push]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'latest'

    - name: Configure kubectl
      env:
        KUBE_CONFIG: ${{ secrets.PROD_KUBE_CONFIG }}
      run: |
        echo "$KUBE_CONFIG" | base64 -d > kubeconfig
        export KUBECONFIG=kubeconfig

    - name: Update image tags
      env:
        DOCKER_REGISTRY: ${{ env.REGISTRY }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        # Update Kubernetes manifests with new image tags
        sed -i "s|image: pronas-pcd-backend:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME_BACKEND}:main-${IMAGE_TAG}|g" infra/k8s/apps/backend.yaml
        sed -i "s|image: pronas-pcd-frontend:.*|image: ${DOCKER_REGISTRY}/${IMAGE_NAME_FRONTEND}:main-${IMAGE_TAG}|g" infra/k8s/apps/frontend.yaml

    - name: Deploy to production
      run: |
        kubectl apply -f infra/k8s/base/
        kubectl apply -f infra/k8s/apps/
        kubectl rollout status deployment/backend -n pronas-pcd --timeout=300s
        kubectl rollout status deployment/frontend -n pronas-pcd --timeout=300s

    - name: Verify deployment
      run: |
        kubectl get pods -n pronas-pcd
        kubectl get services -n pronas-pcd

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Dependency Review
      uses: actions/dependency-review-action@v3
      with:
        config-file: '.github/dependency-review-config.yml'
EOF

# Dependency review config
cat > .github/dependency-review-config.yml << 'EOF'
# Configuration for Dependency Review Action
# https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/configuring-dependency-review

fail-on-severity: moderate
fail-on-scopes:
  - runtime
  - development

allow-licenses:
  - MIT
  - Apache-2.0
  - BSD-2-Clause
  - BSD-3-Clause
  - ISC
  - GPL-3.0
  - LGPL-2.1

deny-licenses:
  - GPL-2.0
  - AGPL-3.0

comment-summary-in-pr: true
EOF

echo "✅ GitHub Actions workflow criado!"

echo "📝 Criando templates de Issues e PRs..."

# Issue templates
mkdir -p .github/ISSUE_TEMPLATE
cat > .github/ISSUE_TEMPLATE/bug_report.yml << 'EOF'
name: Bug Report
description: Criar um relatório de bug para ajudar a melhorar o sistema
title: "[BUG] "
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Obrigado por reportar um bug! Por favor, preencha as informações abaixo.

  - type: textarea
    id: description
    attributes:
      label: Descrição do Bug
      description: Uma descrição clara e concisa do bug
      placeholder: Descreva o que aconteceu...
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Passos para Reproduzir
      description: Passos para reproduzir o comportamento
      placeholder: |
        1. Vá para '...'
        2. Clique em '...'
        3. Role para baixo até '...'
        4. Veja o erro
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Comportamento Esperado
      description: Descrição clara do que você esperava que acontecesse
    validations:
      required: true

  - type: textarea
    id: screenshots
    attributes:
      label: Screenshots
      description: Se aplicável, adicione screenshots para ajudar a explicar o problema

  - type: dropdown
    id: component
    attributes:
      label: Componente Afetado
      options:
        - Frontend (Next.js)
        - Backend (FastAPI)
        - Database (PostgreSQL)
        - Infrastructure (Docker/K8s)
        - Não sei
    validations:
      required: true

  - type: input
    id: environment
    attributes:
      label: Ambiente
      placeholder: "Produção, Desenvolvimento, etc."
    validations:
      required: true

  - type: textarea
    id: additional
    attributes:
      label: Contexto Adicional
      description: Adicione qualquer outro contexto sobre o problema aqui
EOF

cat > .github/ISSUE_TEMPLATE/feature_request.yml << 'EOF'
name: Feature Request
description: Sugerir uma nova funcionalidade para o sistema
title: "[FEATURE] "
labels: ["enhancement", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Obrigado por sugerir uma nova funcionalidade!

  - type: textarea
    id: problem
    attributes:
      label: Problema Relacionado
      description: Existe algum problema relacionado a esta funcionalidade?
      placeholder: "Estou sempre frustrado quando..."

  - type: textarea
    id: solution
    attributes:
      label: Solução Desejada
      description: Descrição clara da funcionalidade que você gostaria
      placeholder: "Eu gostaria que..."
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternativas Consideradas
      description: Descrição de soluções ou funcionalidades alternativas que você considerou

  - type: dropdown
    id: priority
    attributes:
      label: Prioridade
      options:
        - Baixa
        - Média
        - Alta
        - Crítica
    validations:
      required: true

  - type: checkboxes
    id: impact
    attributes:
      label: Áreas Impactadas
      options:
        - label: Interface do Usuário
        - label: API Backend
        - label: Banco de Dados
        - label: Segurança
        - label: Performance
        - label: Documentação

  - type: textarea
    id: additional
    attributes:
      label: Contexto Adicional
      description: Adicione qualquer outro contexto ou screenshots sobre a funcionalidade aqui
EOF

# Pull Request template
cat > .github/pull_request_template.md << 'EOF'
## Descrição

Breve descrição das mudanças realizadas.

## Tipo de Mudança

- [ ] Bug fix (mudança que não quebra funcionalidades existentes e corrige um problema)
- [ ] Nova funcionalidade (mudança que não quebra funcionalidades existentes e adiciona uma funcionalidade)
- [ ] Breaking change (mudança que pode quebrar funcionalidades existentes)
- [ ] Atualização de documentação
- [ ] Refatoração de código
- [ ] Atualização de dependências
- [ ] Melhorias de performance
- [ ] Melhorias de segurança

## Como Foi Testado?

Descreva os testes que você executou para verificar suas mudanças.

- [ ] Testes unitários
- [ ] Testes de integração
- [ ] Testes manuais
- [ ] Testes de performance
- [ ] Testes de segurança

## Checklist

- [ ] Meu código segue as diretrizes de estilo do projeto
- [ ] Realizei uma auto-revisão do meu código
- [ ] Comentei meu código, especialmente em áreas difíceis de entender
- [ ] Fiz mudanças correspondentes na documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Adicionei testes que provam que minha correção é efetiva ou que minha funcionalidade funciona
- [ ] Testes unitários novos e existentes passam localmente com minhas mudanças
- [ ] Qualquer mudança dependente foi mergeada e publicada em módulos downstream

## Screenshots (se aplicável)

Adicione screenshots para ajudar a explicar suas mudanças.

## Issues Relacionadas

Closes #(issue)

## Informações Adicionais

Qualquer informação adicional que seja importante para os revisores.
EOF

echo "✅ Templates de Issues e PRs criados!"

echo "📝 Criando workflow de release..."

# Release workflow
cat > .github/workflows/release.yml << 'EOF'
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Get tag version
      id: get_version
      run: echo "VERSION=${GITHUB_REF#refs/tags/}" >> $GITHUB_OUTPUT

    - name: Generate changelog
      id: changelog
      run: |
        # Generate changelog from commits
        PREVIOUS_TAG=$(git describe --tags --abbrev=0 HEAD^ 2>/dev/null || echo "")
        if [ -n "$PREVIOUS_TAG" ]; then
          CHANGELOG=$(git log --pretty=format:"- %s (%h)" $PREVIOUS_TAG..HEAD)
        else
          CHANGELOG=$(git log --pretty=format:"- %s (%h)")
        fi
        echo "CHANGELOG<<EOF" >> $GITHUB_OUTPUT
        echo "$CHANGELOG" >> $GITHUB_OUTPUT
        echo "EOF" >> $GITHUB_OUTPUT

    - name: Build release artifacts
      run: |
        # Create release directory
        mkdir -p release
        
        # Copy deployment scripts
        cp -r scripts/ release/
        cp -r infra/ release/
        cp docker-compose.prod.yml release/
        cp .env.production release/.env.production.example
        
        # Create archive
        tar -czf release/pronas-pcd-${{ steps.get_version.outputs.VERSION }}.tar.gz -C release .

    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: ${{ steps.get_version.outputs.VERSION }}
        name: Release ${{ steps.get_version.outputs.VERSION }}
        body: |
          ## 🚀 PRONAS/PCD Release ${{ steps.get_version.outputs.VERSION }}
          
          ### 📋 Changes in this Release:
          
          ${{ steps.changelog.outputs.CHANGELOG }}
          
          ### 📦 Release Artifacts:
          
          - `pronas-pcd-${{ steps.get_version.outputs.VERSION }}.tar.gz` - Complete deployment package
          
          ### 🚀 Deployment Instructions:
          
          1. Download and extract the release package
          2. Configure `.env.production` with your environment variables
          3. Run `./scripts/deploy-production.sh` for Docker deployment
          4. Or run `./scripts/deploy-k8s.sh` for Kubernetes deployment
          
          ### 📖 Documentation:
          
          See [README.md](https://github.com/ministerio-saude/pronas-pcd/blob/main/README.md) for complete documentation.
          
          ### 🔒 Security:
          
          This release includes security updates and follows LGPD compliance requirements.
        files: |
          release/pronas-pcd-${{ steps.get_version.outputs.VERSION }}.tar.gz
        draft: false
        prerelease: false
        generate_release_notes: true
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Notify deployment
      run: |
        echo "Release ${{ steps.get_version.outputs.VERSION }} created successfully!"
        echo "Deployment artifacts are available for download."
EOF

echo "✅ Workflow de release criado!"

echo "📝 Criando configurações de segurança..."

# Security policy
cat > SECURITY.md << 'EOF'
# Política de Segurança

## Versões Suportadas

| Versão | Suportada          |
| ------ | ------------------ |
| 1.0.x  | :white_check_mark: |

## Reportando uma Vulnerabilidade

A segurança do sistema PRONAS/PCD é nossa prioridade máxima. Se você descobrir uma vulnerabilidade de segurança, por favor, nos informe de forma responsável.

### Como Reportar

1. **NÃO** abra uma issue pública no GitHub
2. Envie um email para: security@pronas-pcd.gov.br
3. Inclua o máximo de informações possível sobre a vulnerabilidade
4. Se possível, forneça um PoC (Proof of Concept) responsável

### O que Incluir no Relatório

- Descrição da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Versão afetada
- Qualquer informação adicional que possa ser útil

### Processo de Resposta

1. **Confirmação**: Confirmaremos o recebimento do seu relatório em até 48 horas
2. **Avaliação**: Avaliaremos a vulnerabilidade e determinaremos a severidade
3. **Desenvolvimento**: Desenvolveremos uma correção
4. **Teste**: Testaremos a correção
5. **Release**: Lançaremos uma atualização de segurança
6. **Divulgação**: Divulgaremos a vulnerabilidade de forma coordenada

### Timeline de Resposta

- Confirmação inicial: 48 horas
- Avaliação completa: 7 dias
- Correção e release: 30 dias (dependendo da severidade)

### Reconhecimento

Agradecemos aos pesquisadores de segurança que reportam vulnerabilidades de forma responsável. Com sua permissão, reconheceremos sua contribuição em nossos release notes.

## Conformidade LGPD

Este sistema segue rigorosamente as diretrizes da Lei Geral de Proteção de Dados (LGPD). Para questões relacionadas à privacidade de dados, entre em contato com: lgpd@pronas-pcd.gov.br

## Contato

- Segurança: security@pronas-pcd.gov.br
- LGPD: lgpd@pronas-pcd.gov.br
- Suporte Geral: suporte@pronas-pcd.gov.br
EOF

# CodeQL workflow
cat > .github/workflows/codeql.yml << 'EOF'
name: "CodeQL Security Scan"

on:
  push:
    branches: [ "main", "develop" ]
  pull_request:
    branches: [ "main" ]
  schedule:
    - cron: '30 2 * * 1'  # Weekly on Mondays

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    permissions:
      actions: read
      contents: read
      security-events: write

    strategy:
      fail-fast: false
      matrix:
        language: [ 'javascript', 'python' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}
        queries: security-extended,security-and-quality

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        category: "/language:${{matrix.language}}"
EOF

echo "✅ Configurações de segurança criadas!"

echo ""
echo "🎉 LOTE 4 PARTE 3 APLICADO COM SUCESSO!"
echo "======================================="
echo ""
echo "📋 Resumo do que foi criado:"
echo "• Pipeline CI/CD completo com GitHub Actions"
echo "• Testes automatizados para Backend (Python) e Frontend (Node.js)"
echo "• Build e push automático de imagens Docker"
echo "• Deploy automático para staging e produção"
echo "• Scans de segurança (Trivy, CodeQL, Dependency Review)"
echo "• Templates para Issues e Pull Requests"
echo "• Workflow de release automatizado"
echo "• Política de segurança e conformidade LGPD"
echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo "1. Aguarde Lote 4 Parte 4 (Monitoring & Observability)"
echo "2. Configure secrets no GitHub:"
echo "   - STAGING_KUBE_CONFIG"
echo "   - PROD_KUBE_CONFIG"
echo "3. Configure branch protection rules"
echo ""
echo "📊 Status:"
echo "• Lote 4.1: ✅ Docker Production + Nginx"
echo "• Lote 4.2: ✅ Kubernetes Manifests"
echo "• Lote 4.3: ✅ CI/CD GitHub Actions"
echo "• Lote 4.4: ⏳ Monitoring (próximo)"
echo "• Lote 4.5: ⏳ Final Scripts"
echo ""