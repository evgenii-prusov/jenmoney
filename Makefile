.PHONY: help dev dev-backend dev-frontend stop-all clean-ports lint format typecheck test db-init db-clean clean install-backend install-frontend install-pre-commit setup pr-check branch-new branch-sync

# Default target
help: ## Show this help message
	@echo "JenMoney Development Commands"
	@echo ""
	@echo "Quick start:"
	@echo "  make setup    # Initial setup (install deps + init db)"
	@echo "  make dev      # Start both frontend and backend"
	@echo "  make stop-all # Stop all servers"
	@echo ""
	@echo "All commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# ============ Development Commands ============
dev: ## Start both frontend and backend servers
	@if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null; then \
		echo "Backend already running on port 8000"; \
	else \
		echo "Starting backend server..."; \
		make dev-backend & \
	fi
	@if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null; then \
		echo "Frontend already running on port 5173"; \
	else \
		sleep 2; \
		echo "Starting frontend server..."; \
		make dev-frontend; \
	fi

dev-backend: ## Start backend server only (port 8000)
	cd backend && uv run uvicorn jenmoney.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend server only (port 5173)
	cd frontend && npm run dev

stop-all: ## Stop all development servers
	@echo "Stopping all development servers..."
	@pkill -f "uvicorn jenmoney.main:app" || echo "Backend server not running"
	@pkill -f "vite" || echo "Frontend server not running"

clean-ports: ## Force kill processes on ports 8000 and 5173
	@echo "Cleaning up development ports..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Port 8000 is free"
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "Port 5173 is free"

# ============ Code Quality (Pre-commit integrated) ============
lint: ## Run ruff linter on backend code
	cd backend && uv run ruff check src/

format: ## Format backend code with ruff
	cd backend && uv run ruff format src/

typecheck: ## Run type checking with mypy
	cd backend && uv run mypy src/

test: ## Run backend tests
	cd backend && uv run pytest -v

# ============ Database ============
db-init: ## Initialize database (SQLite or PostgreSQL based on DATABASE_URL)
	cd backend && uv run python -c "from jenmoney.database import init_db; init_db()"

db-clean: ## Delete SQLite database file (data loss!)
	rm -f backend/data/finance.db

db-postgres-start: ## Start PostgreSQL using Docker
	@echo "Starting PostgreSQL in Docker..."
	docker run --name jenmoney-postgres -d \
		-e POSTGRES_USER=jenmoney \
		-e POSTGRES_PASSWORD=jenmoney \
		-e POSTGRES_DB=jenmoney \
		-p 5432:5432 \
		postgres:15-alpine || echo "PostgreSQL container already exists"

db-postgres-stop: ## Stop PostgreSQL Docker container
	@echo "Stopping PostgreSQL container..."
	docker stop jenmoney-postgres || echo "Container not running"

db-postgres-clean: ## Remove PostgreSQL Docker container (data loss!)
	@echo "Removing PostgreSQL container..."
	docker stop jenmoney-postgres 2>/dev/null || true
	docker rm jenmoney-postgres 2>/dev/null || true

db-postgres-logs: ## Show PostgreSQL container logs
	docker logs jenmoney-postgres

db-migrate: ## Migrate data from SQLite to PostgreSQL
	cd backend && uv run python scripts/migrate_sqlite_to_postgres.py

# ============ Setup & Installation ============
setup: ## Complete project setup (deps + database)
	@echo "Setting up JenMoney project..."
	@make install-backend
	@make install-frontend
	@make install-pre-commit
	@make db-init
	@echo ""
	@echo "✅ Setup complete! Run 'make dev' to start."

install-backend: ## Install Python dependencies
	cd backend && uv sync --dev

install-frontend: ## Install Node dependencies
	cd frontend && npm install

install-pre-commit: ## Install pre-commit hooks
	cd backend && uv run pre-commit install

# ============ Cleanup ============
clean: ## Clean cache files and build artifacts
	@echo "Cleaning cache files..."
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	find backend -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf frontend/dist frontend/node_modules/.vite 2>/dev/null || true

# ============ Git Workflow Helpers ============
pr-check: ## Run all checks before creating PR
	@echo "Running PR readiness checks..."
	@echo "1. Formatting code..."
	@make format
	@echo "2. Running linter..."
	@make lint
	@echo "3. Type checking..."
	@make typecheck
	@echo "4. Running tests..."
	@make test
	@echo ""
	@echo "✅ All checks passed! Ready to create PR."

branch-new: ## Create new feature branch (usage: make branch-new name=feature-name)
	@if [ -z "$(name)" ]; then \
		echo "Error: Please provide branch name. Usage: make branch-new name=feature-name"; \
		exit 1; \
	fi
	@echo "Creating new feature branch: feat/$(name)"
	@git checkout master
	@git pull origin master
	@git checkout -b feat/$(name)
	@echo "✅ Branch feat/$(name) created and checked out"

branch-sync: ## Sync current branch with master
	@echo "Syncing with master..."
	@git fetch origin
	@git rebase origin/master
	@echo "✅ Branch synced with master"