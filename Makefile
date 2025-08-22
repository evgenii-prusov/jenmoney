.PHONY: help dev dev-backend dev-frontend dev-all build build-frontend server stop stop-all stop-backend stop-frontend lint format format-check typecheck check test test-cov test-fast db-init db-clean clean clean-all install install-backend install-frontend setup reset

# Default target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Development Commands
dev: dev-all ## Start both backend and frontend development servers (alias for dev-all)

dev-all: stop-all clean-ports ## Start both backend and frontend development servers
	@echo "Starting all development servers..."
	@make dev-backend &
	@sleep 2
	@make dev-frontend

dev-backend: ## Start backend development server with hot reload
	@echo "Starting backend development server..."
	cd backend && uv run uvicorn jenmoney.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

# Build Commands
build: build-frontend ## Build production assets (alias for build-frontend)

build-frontend: ## Build frontend for production
	@echo "Building frontend for production..."
	cd frontend && npm run build

# Server Management
server: ## Start backend production server
	@echo "Starting backend production server..."
	cd backend && uv run uvicorn jenmoney.main:app --host 0.0.0.0 --port 8000

stop: stop-all ## Stop all development servers (alias for stop-all)

stop-all: ## Stop all development servers
	@echo "Stopping all development servers..."
	@pkill -f "uvicorn jenmoney.main:app" || echo "Backend server not running"
	@pkill -f "vite" || echo "Frontend server not running"

stop-backend: ## Stop backend development server
	@echo "Stopping backend development server..."
	@pkill -f "uvicorn jenmoney.main:app" || echo "Backend server not running"

stop-frontend: ## Stop frontend development server
	@echo "Stopping frontend development server..."
	@pkill -f "vite" || echo "Frontend server not running"

clean-ports: ## Kill processes using development ports (8000, 5173)
	@echo "Cleaning up development ports..."
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || echo "Port 8000 is free"
	@lsof -ti:5173 | xargs kill -9 2>/dev/null || echo "Port 5173 is free"

stop-clean: clean-ports stop-all ## Stop all servers and clean up ports

# Code Quality
lint: ## Run ruff linter
	@echo "Running ruff linter..."
	cd backend && uv run ruff check src/

format: ## Format code with ruff
	@echo "Formatting code..."
	cd backend && uv run ruff format src/

format-check: ## Check code formatting without modifying
	@echo "Checking code format..."
	cd backend && uv run ruff format --check src/

typecheck: ## Run mypy type checker
	@echo "Running type checker..."
	cd backend && uv run mypy src/

check: ## Run all static checks (lint + format check + typecheck)
	@echo "Running all static checks..."
	@make lint
	@make format-check
	@make typecheck

# Testing
test: ## Run all tests with verbose output
	@echo "Running tests..."
	cd backend && uv run pytest -v

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	cd backend && uv run pytest --cov=jenmoney --cov-report=term-missing

test-fast: ## Run tests without verbose output
	@echo "Running tests (fast)..."
	cd backend && uv run pytest

# Database
db-init: ## Initialize database
	@echo "Initializing database..."
	cd backend && uv run python -c "from jenmoney.database import init_db; init_db()"

db-clean: ## Remove database file
	@echo "Removing database file..."
	rm -f backend/data/finance.db

# Utility Commands
clean: ## Clean up cache files and build directories
	@echo "Cleaning up backend cache..."
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	find backend -type f -name "*.pyo" -delete 2>/dev/null || true
	find backend -type f -name ".coverage" -delete 2>/dev/null || true
	@echo "Cleaning up frontend build..."
	rm -rf frontend/dist frontend/node_modules/.vite 2>/dev/null || true

clean-all: clean ## Deep clean including node_modules and virtual environments
	@echo "Deep cleaning..."
	rm -rf frontend/node_modules backend/.venv backend/venv 2>/dev/null || true

# Installation Commands
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies including dev
	@echo "Installing backend dependencies..."
	cd backend && uv sync --dev

install-frontend: ## Install frontend dependencies
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Quick Setup Commands
setup: ## Initial project setup (install + db init)
	@echo "Setting up project..."
	@make install
	@make db-init
	@echo "Setup complete! Run 'make dev' to start development servers."

reset: ## Reset the project (clean + setup)
	@echo "Resetting project..."
	@make clean-all
	@make db-clean
	@make setup