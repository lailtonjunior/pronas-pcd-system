.PHONY: help setup dev test lint build clean docker-build docker-up docker-down migrate seed backup

# Default target
help: ## Show this help message
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development Setup
setup: ## Initial project setup
	@echo "Setting up PRONAS/PCD System..."
	@./scripts/setup.sh

dev: ## Start development environment
	@echo "Starting development environment..."
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

dev-logs: ## Show development logs
	@docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f

# Testing
test: ## Run all tests
	@echo "Running tests..."
	@./scripts/test.sh

test-backend: ## Run backend tests only
	@echo "Running backend tests..."
	@cd backend && python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests only
	@echo "Running frontend tests..."
	@cd frontend && npm run test

test-e2e: ## Run end-to-end tests
	@echo "Running E2E tests..."
	@cd frontend && npm run test:e2e

# Code Quality
lint: ## Run linting for all projects
	@echo "Running linting..."
	@./scripts/lint.sh

lint-backend: ## Run backend linting
	@cd backend && python -m black . && python -m isort . && python -m flake8 .

lint-frontend: ## Run frontend linting
	@cd frontend && npm run lint && npm run format

# Build
build: ## Build all services
	@echo "Building all services..."
	@./scripts/build.sh

build-backend: ## Build backend image
	@docker build -f backend/Dockerfile -t pronas-pcd-backend:latest ./backend

build-frontend: ## Build frontend image
	@docker build -f frontend/Dockerfile -t pronas-pcd-frontend:latest ./frontend

# Docker Management
docker-up: ## Start all services with Docker Compose
	@docker-compose up -d

docker-up-prod: ## Start production services
	@docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

docker-down: ## Stop all services
	@docker-compose down

docker-clean: ## Remove all containers, networks, and volumes
	@docker-compose down -v --remove-orphans
	@docker system prune -f

# Database Operations
migrate: ## Run database migrations
	@echo "Running database migrations..."
	@./scripts/migrate.sh

migrate-create: ## Create new migration
	@echo "Creating new migration..."
	@cd backend && alembic revision --autogenerate -m "$(name)"

seed: ## Seed database with initial data
	@echo "Seeding database..."
	@./scripts/seed.sh

backup: ## Create database backup
	@echo "Creating database backup..."
	@./scripts/backup.sh

# Production
deploy: ## Deploy to production
	@echo "Deploying to production..."
	@./scripts/deploy.sh

# Clean
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@cd backend && rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true
