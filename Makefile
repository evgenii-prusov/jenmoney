.PHONY: help dev server stop lint format format-check typecheck check test test-cov test-fast db-init db-clean clean install

# Default target
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

# Server Management
dev: ## Start development server with hot reload
	@echo "Starting development server..."
	cd backend && uvicorn jenmoney.main:app --reload --host 0.0.0.0 --port 8000

server: ## Start production server
	@echo "Starting production server..."
	cd backend && uvicorn jenmoney.main:app --host 0.0.0.0 --port 8000

stop: ## Stop the development server
	@echo "Stopping development server..."
	@pkill -f "uvicorn jenmoney.main:app" || echo "Server not running"

# Code Quality
lint: ## Run ruff linter
	@echo "Running ruff linter..."
	cd backend && ruff check src/

format: ## Format code with ruff
	@echo "Formatting code..."
	cd backend && ruff format src/

format-check: ## Check code formatting without modifying
	@echo "Checking code format..."
	cd backend && ruff format --check src/

typecheck: ## Run mypy type checker
	@echo "Running type checker..."
	cd backend && mypy src/

check: ## Run all static checks (lint + format check + typecheck)
	@echo "Running all static checks..."
	@make lint
	@make format-check
	@make typecheck

# Testing
test: ## Run all tests with verbose output
	@echo "Running tests..."
	cd backend && pytest -v

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	cd backend && pytest --cov=jenmoney --cov-report=term-missing

test-fast: ## Run tests without verbose output
	@echo "Running tests (fast)..."
	cd backend && pytest

# Database
db-init: ## Initialize database
	@echo "Initializing database..."
	cd backend && python -c "from jenmoney.database import init_db; init_db()"

db-clean: ## Remove database file
	@echo "Removing database file..."
	rm -f backend/data/finance.db

# Utility Commands
clean: ## Clean up cache files and directories
	@echo "Cleaning up..."
	find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find backend -type f -name "*.pyc" -delete 2>/dev/null || true
	find backend -type f -name "*.pyo" -delete 2>/dev/null || true
	find backend -type f -name ".coverage" -delete 2>/dev/null || true

install: ## Install all dependencies including dev
	@echo "Installing dependencies..."
	cd backend && pip install -e ".[dev]"