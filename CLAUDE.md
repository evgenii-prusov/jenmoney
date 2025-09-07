# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JenMoney is a personal finance management application with a FastAPI backend and React frontend. The application manages financial accounts with real-time balance updates.

## Python Environment Management

**IMPORTANT**: All Python virtual environment operations, dependency installations, and tool installations (like ruff, pytest, mypy, etc.) must be performed using `uv`. This includes:
- Creating and managing virtual environments
- Installing Python dependencies
- Installing development tools
- Managing Python versions

## Pre-commit Hooks

The project uses pre-commit framework to automatically run quality checks before commits:

**IMPORTANT**: You are NOT allowed to skip pre-commit hooks (using `--no-verify`) unless explicitly requested by the user. All commits must pass pre-commit checks.

### Configured Hooks
- **ruff**: Linting and auto-fixing Python code issues
- **ruff-format**: Code formatting  
- **mypy**: Type checking
- **pytest**: Running all tests

### Pre-commit Commands
```bash
# Install pre-commit hooks (run from backend directory)
uv run pre-commit install

# Run hooks manually on all files
cd backend && uv run pre-commit run --all-files

# Update hook versions
cd backend && uv run pre-commit autoupdate
```

Note: All hooks must pass for a commit to succeed. Fix any issues reported by the hooks before committing.

## Development Commands

### Quick Start
```bash
# Initial setup (installs dependencies and initializes database)
make setup

# Start both backend and frontend development servers
make dev

# Stop all servers
make stop-all
```

**IMPORTANT: Server Management Rules**
- ALWAYS check if servers are already running before starting them
- Use `make stop-all` to stop all servers before starting new ones
- Use `make clean-ports` if ports are stuck
- NEVER start servers directly with `uv run` or `npm run` - ALWAYS use Makefile commands
- NEVER use `npm run dev`, `npm run build`, etc. - ALWAYS use `make dev-frontend`, `make dev-backend`, etc.
- The `make dev` command is smart and checks if servers are already running

### Development Servers
```bash
make dev           # Start both frontend and backend (smart - checks if already running)
make dev-backend   # Start backend only on http://localhost:8000
make dev-frontend  # Start frontend only on http://localhost:5173
make stop-all      # Stop all development servers
make clean-ports   # Force kill processes on ports 8000 and 5173
```

### Code Quality (Pre-commit integrated)

**IMPORTANT: Always use Makefile commands for code quality checks**
- NEVER run `ruff`, `mypy`, `pytest` directly
- ALWAYS use the Makefile commands below:

```bash
make lint          # Run ruff linter on backend code
make format        # Format backend code with ruff (auto-fixes issues)
make typecheck     # Run type checking with mypy
make test          # Run backend tests with pytest
make pr-check      # Run all checks before creating a PR

# Note: format-check and other checks are handled by pre-commit hooks
```

### Database Management

**Database Support**: JenMoney supports both SQLite (default) and PostgreSQL databases.

```bash
# SQLite (default)
make db-init       # Initialize SQLite database
make db-clean      # Delete SQLite database file (data loss warning!)

# PostgreSQL (production-ready)
make db-postgres-start   # Start PostgreSQL using Docker
make db-postgres-stop    # Stop PostgreSQL Docker container
make db-postgres-clean   # Remove PostgreSQL container (data loss!)
make db-postgres-logs    # Show PostgreSQL container logs
make db-migrate          # Migrate data from SQLite to PostgreSQL
```

**Configuration**: Set `DATABASE_URL` environment variable:
- SQLite: `sqlite:///./data/finance.db` (default)
- PostgreSQL: `postgresql://jenmoney:jenmoney@localhost:5432/jenmoney`

For detailed PostgreSQL setup and migration, see `docs/POSTGRESQL_MIGRATION.md`.

### Setup & Installation
```bash
make setup            # Complete project setup (deps + database)
make install-backend  # Install Python dependencies with uv
make install-frontend # Install Node dependencies with npm
```

### Cleanup
```bash
make clean         # Clean cache files and build artifacts
```

### Frontend Commands (Direct npm)
```bash
# Run from frontend directory
npm run dev        # Start dev server
npm run build      # Build for production
npm run preview    # Preview production build
```

## Architecture

### Backend Structure (FastAPI + SQLAlchemy)

The backend follows a layered architecture:

1. **API Layer** (`backend/src/jenmoney/api/`): FastAPI routers and endpoints
   - Version-prefixed routing (`/api/v1`)
   - RESTful endpoints for CRUD operations

2. **Business Logic** (`backend/src/jenmoney/crud/`): Repository pattern for database operations
   - Base CRUD class with generic operations
   - Model-specific CRUD classes inheriting from base

3. **Data Layer**:
   - **Models** (`backend/src/jenmoney/models/`): SQLAlchemy ORM models
   - **Schemas** (`backend/src/jenmoney/schemas/`): Pydantic models for validation and serialization
   - **Database** (`backend/src/jenmoney/database.py`): Session management and initialization

4. **Configuration** (`backend/src/jenmoney/config.py`): Pydantic Settings with environment variable support
   - Prefix: `JENMONEY_` for backend env vars

### Frontend Structure (React + TypeScript)

The frontend uses a feature-based architecture:

1. **API Integration** (`frontend/src/api/`):
   - Axios client with base URL configuration
   - Type-safe API service functions

2. **State Management**: TanStack React Query
   - Custom hooks in `frontend/src/hooks/`
   - 5-second auto-refresh for real-time updates
   - Optimistic updates for better UX

3. **UI Components**:
   - **Layouts**: App-level layout components
   - **Components**: Reusable UI components (cards, forms, dialogs)
   - **Features**: Feature-specific components (`features/accounts/`)

4. **Theming**: Material UI with Solarized Light theme
   - Theme configuration in `frontend/src/theme/`

### Environment Configuration

Environment variables are centralized in the project root:
- `.env` file in root directory (ignored by git)
- `.env.example` for reference
- Frontend uses `VITE_` prefix
- Backend uses `JENMONEY_` prefix or reads directly
- Vite config points to parent directory for env files

### Database

**Supported Databases**:
- **SQLite**: Default for development (`backend/data/finance.db`)
- **PostgreSQL**: Recommended for production (configurable via `DATABASE_URL`)

**Features**:
- Models use SQLAlchemy ORM with autoincrement IDs
- Database-agnostic code supports both SQLite and PostgreSQL
- Migration script available for SQLite → PostgreSQL transition
- Alembic for schema migrations (when needed)

## Key Technical Decisions

1. **Type Safety**: Full TypeScript in frontend, strict mypy in backend
2. **Real-time Updates**: React Query with 5-second refetch interval
3. **Optimistic Updates**: Immediate UI feedback with rollback on error
4. **Modal Forms**: Create/Edit operations use Material UI dialogs
5. **Card Layout**: Accounts displayed as cards, not tables
6. **No Authentication**: Currently no auth implementation (planned for future)

## Multicurrency Support

The application supports multiple currencies (EUR, USD, RUB, JPY) with automatic conversion:

### Features
- **Currency Conversion**: Accounts show both original and converted balances
- **Default Currency**: Users can set their preferred display currency
- **Exchange Rates**: Manual management via CSV/JSON import
- **Total Portfolio Value**: Calculated across all accounts in default currency

### Exchange Rate Management
- Rates stored in `backend/data/currency_rates.csv`
- All rates are stored as conversions to USD
- Cross-currency conversion goes through USD (e.g., EUR→RUB = EUR→USD→RUB)
- Import rates via API endpoints or directly update CSV file

### Database Tables
- `accounts`: Financial accounts with currency field
- `currency_rates`: Exchange rates with effective dates
- `transfers`: Money transfers between accounts with multi-currency support
- `user_settings`: User preferences including default currency

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

### Accounts
- `GET /accounts/` - List all accounts (paginated, with currency conversion)
- `POST /accounts/` - Create new account
- `GET /accounts/{id}` - Get specific account
- `PATCH /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account
- `GET /accounts/total-balance/` - Get total portfolio value in default currency

### Transfers
- `GET /transfers/` - List all transfers (paginated, with optional account filtering)
- `POST /transfers/` - Create new transfer between accounts
- `GET /transfers/{id}` - Get specific transfer
- `PATCH /transfers/{id}` - Update transfer status or description

### Settings
- `GET /settings/` - Get user settings (including default currency)
- `PATCH /settings/` - Update user settings

### Currency Rates
- `GET /currency-rates/` - List all exchange rates
- `GET /currency-rates/current` - Get current exchange rates to USD
- `POST /currency-rates/import/csv` - Import rates from CSV file
- `POST /currency-rates/import/json` - Import rates from JSON file

Note: All POST endpoints require trailing slash to avoid 307 redirects.

## Common Issues and Solutions

1. **Backend ID constraint error**: Ensure `autoincrement=True` on ID columns and recreate DB with `make db-clean && make db-init`

2. **Frontend env variables not loading**: Check that `vite.config.ts` has `envDir: resolve(__dirname, '..')` 

3. **Port already in use**: Use `make stop-all` to kill all servers, or `make clean-ports` for force kill

4. **TypeScript errors in vite.config**: Install `@types/node` as dev dependency

5. **Servers already running**: The improved `make dev` command now checks if servers are already running and skips starting them again

## Testing Approach

- Backend: pytest with fixtures for database sessions
- Frontend: Component testing with React Testing Library (when implemented)
- E2E: Manual testing via `make dev` for full stack

## Git Workflow

**IMPORTANT**: Follow the feature branch workflow. Do not commit directly to master.

**ALWAYS CREATE A FEATURE BRANCH BEFORE STARTING WORK**:
Use `make branch-new name=<feature-name>` to create and switch to a new feature branch.
This command will automatically:
- Create a branch with the correct naming convention (feat/, fix/, etc.)
- Sync with the latest master
- Switch to the new branch

### Branch Naming
- `feat/` - New features
- `fix/` - Bug fixes  
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test updates
- `chore/` - Maintenance tasks

### Workflow Steps
1. Create feature branch from master: `git checkout -b feat/feature-name`
2. Make changes and commit with conventional commit messages
3. Push branch to remote: `git push -u origin feat/feature-name`
4. Create pull request on GitHub
5. After merge, delete feature branch

### Commit Message Format
```
<type>(<scope>): <subject>
```

Examples:
- `feat: Add account export functionality`
- `fix(api): Correct balance calculation`
- `docs: Update API documentation`

See `docs/GIT_WORKFLOW.md` for detailed guidelines.