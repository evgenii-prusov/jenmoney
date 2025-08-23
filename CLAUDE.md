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

### Development Servers
```bash
make dev           # Start both frontend and backend (smart - checks if already running)
make dev-backend   # Start backend only on http://localhost:8000
make dev-frontend  # Start frontend only on http://localhost:5173
make stop-all      # Stop all development servers
make clean-ports   # Force kill processes on ports 8000 and 5173
```

### Code Quality (Pre-commit integrated)
```bash
make lint          # Run ruff linter on backend code
make format        # Format backend code with ruff
make typecheck     # Run type checking with mypy
make test          # Run backend tests with pytest

# Note: format-check and other checks are handled by pre-commit hooks
```

### Database Management
```bash
make db-init       # Initialize SQLite database
make db-clean      # Delete database file (data loss warning!)
```

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

- SQLite for development (file: `backend/data/finance.db`)
- Models use SQLAlchemy ORM with autoincrement IDs
- Alembic for migrations (when needed)

## Key Technical Decisions

1. **Type Safety**: Full TypeScript in frontend, strict mypy in backend
2. **Real-time Updates**: React Query with 5-second refetch interval
3. **Optimistic Updates**: Immediate UI feedback with rollback on error
4. **Modal Forms**: Create/Edit operations use Material UI dialogs
5. **Card Layout**: Accounts displayed as cards, not tables
6. **No Authentication**: Currently no auth implementation (planned for future)

## API Endpoints

Base URL: `http://localhost:8000/api/v1`

- `GET /accounts/` - List all accounts (paginated)
- `POST /accounts/` - Create new account
- `GET /accounts/{id}` - Get specific account
- `PATCH /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account

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