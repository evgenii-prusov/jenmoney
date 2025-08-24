# Jenmoney - Personal Finance Management Application

This is a personal finance application for tracking multiple currency accounts with real-time exchange rate conversion. Built as a Single Page Application (SPA) with React + Material UI frontend and FastAPI backend.

## Architecture Overview

```
jenmoney/
├── backend/          # FastAPI backend
│   ├── src/jenmoney/ # Source code
│   │   ├── api/      # API endpoints (versioned /api/v1/)
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── crud/     # Repository pattern for database operations
│   │   ├── database.py # Session management and initialization
│   │   └── config.py   # Pydantic Settings (JENMONEY_ prefix)
│   ├── tests/        # Pytest tests
│   └── data/         # SQLite database location
├── frontend/         # React + Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/      # Custom React hooks (TanStack Query)
│   │   ├── api/        # API client (Axios)
│   │   ├── features/   # Feature-specific components (accounts/)
│   │   ├── theme/      # Material UI Solarized Light theme
│   │   └── types/      # TypeScript types
│   └── tests/
├── docs/             # Documentation (including GIT_WORKFLOW.md)
├── scripts/          # Utility scripts
├── .copilot/         # GitHub Copilot instructions
├── Makefile          # Common operations (ALWAYS use these commands)
├── .env.example      # Environment variable template
└── CLAUDE.md         # Claude-specific development guidance
```

## Core Features & User Flow

1. **Account Management**: Users can create, edit, delete, and view multiple currency accounts
2. **Multi-currency Support**: Each account has a native currency; amounts are displayed in both native and default currency
3. **Real-time Updates**: TanStack Query with 5-second auto-refresh for live currency conversion
4. **Total Balance**: Header displays aggregate balance in user's default currency
5. **Exchange Rate Management**: Manual import via CSV/JSON with rates stored as conversions to USD
6. **Currency Conversion**: Cross-currency conversion goes through USD (EUR→RUB = EUR→USD→RUB)

### Database Tables
- `accounts`: Financial accounts with currency field
- `currency_rates`: Exchange rates with effective dates  
- `user_settings`: User preferences including default currency

### API Endpoints
Base URL: `http://localhost:8000/api/v1`

**Accounts:**
- `GET /accounts/` - List all accounts (paginated, with currency conversion)
- `POST /accounts/` - Create new account
- `GET /accounts/{id}` - Get specific account
- `PATCH /accounts/{id}` - Update account
- `DELETE /accounts/{id}` - Delete account
- `GET /accounts/total-balance/` - Get total portfolio value in default currency

**Settings:**
- `GET /settings/` - Get user settings (including default currency)
- `PATCH /settings/` - Update user settings

**Currency Rates:**
- `GET /currency-rates/` - List all exchange rates
- `GET /currency-rates/current` - Get current exchange rates to USD
- `POST /currency-rates/import/csv` - Import rates from CSV file
- `POST /currency-rates/import/json` - Import rates from JSON file

⚠️ **Important**: All POST endpoints require trailing slash to avoid 307 redirects.

## Tech Stack & Dependencies

### Backend (Python 3.13+)
- **Framework**: FastAPI with async support
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Package Manager**: uv (MANDATORY - never use pip directly)
- **Testing**: pytest with pytest-asyncio
- **Linting**: ruff (configured in pyproject.toml)

**CRITICAL**: All Python operations MUST use `uv`:
- Virtual environments: `uv venv`, not `python -m venv`
- Dependencies: `uv add`, not `pip install`
- Running tools: `uv run pytest`, not direct command execution

### Frontend (Node 20+)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI with Solarized Light theme
- **State Management**: TanStack Query v5
- **API Client**: Axios or native fetch

## Code Examples & Patterns

### Backend API Endpoint Pattern
```python
# filepath: backend/src/api/v1/accounts.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])

@router.get("/", response_model=list[AccountResponse])
async def get_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> list[Account]:
    """Get all accounts for the current user."""
    return await AccountService.get_user_accounts(db, current_user.id)
```

### Frontend Component Pattern
```typescript
// filepath: frontend/src/components/AccountCard.tsx
import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, Typography } from '@mui/material';

export const AccountCard: React.FC<{ accountId: string }> = ({ accountId }) => {
  const { data: account } = useQuery({
    queryKey: ['account', accountId],
    queryFn: () => api.getAccount(accountId),
    refetchInterval: 5000, // 5-second auto-refresh
  });
  
  // Component implementation
};
```

### Database Model Pattern
```python
# filepath: backend/src/models/account.py
from sqlalchemy import Column, String, Decimal, ForeignKey
from sqlalchemy.orm import relationship

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    balance = Column(Decimal(10, 2), default=0)
    currency = Column(String(3), nullable=False)  # ISO 4217 code
    user_id = Column(String, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="accounts")
```

## Coding Standards & Conventions

### Python
- Use modern Python 3.13+ features (pattern matching, union types, etc.)
- Follow PEP 8 with ruff configuration
- Use type hints for all function signatures
- Async/await for all database operations
- Descriptive variable names: `user_accounts` not `ua`
- **CRITICAL**: Always use `uv` for dependency management and tool execution

### TypeScript/React
- Functional components with TypeScript
- Custom hooks for shared logic  
- Interfaces over types for object shapes
- Descriptive component names: `AccountListHeader` not `Header`
- Use TanStack Query for state management with 5-second auto-refresh
- Material UI components with Solarized Light theme

### API Design
- RESTful endpoints with proper HTTP methods
- Versioned API: `/api/v1/`
- Consistent response format:
  ```json
  {
    "data": {...},
    "message": "Success", 
    "timestamp": "2024-01-01T00:00:00Z"
  }
  ```
- **CRITICAL**: All POST endpoints require trailing slash

### Architecture Patterns
- **Backend**: Layered architecture with API/CRUD/Models separation
- **Frontend**: Feature-based architecture with components/hooks/api separation
- **Database**: SQLAlchemy ORM with autoincrement IDs, repository pattern
- **State**: TanStack Query with optimistic updates and real-time refresh

## Error Handling & Logging

```python
# Backend error handling
try:
    result = await account_service.create_account(db, account_data)
except ValueError as e:
    logger.error(f"Invalid account data: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

```typescript
// Frontend error handling
const mutation = useMutation({
  mutationFn: createAccount,
  onError: (error) => {
    console.error('Failed to create account:', error);
    showNotification({ type: 'error', message: 'Failed to create account' });
  },
});
```

## Testing Guidelines

### Backend Testing
```python
# filepath: backend/tests/test_accounts.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_account(client: AsyncClient, auth_headers: dict):
    """Test account creation with valid data."""
    response = await client.post(
        "/api/v1/accounts",
        json={"name": "Savings", "currency": "USD", "balance": 1000},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["data"]["currency"] == "USD"
```

### Frontend Testing
```typescript
// filepath: frontend/src/components/__tests__/AccountCard.test.tsx
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

test('displays account balance in both currencies', () => {
  render(
    <QueryClientProvider client={queryClient}>
      <AccountCard accountId="123" />
    </QueryClientProvider>
  );
  
  expect(screen.getByText(/USD 1,000/)).toBeInTheDocument();
  expect(screen.getByText(/EUR 850/)).toBeInTheDocument();
});
```

## Development Workflow & Commands

**CRITICAL**: Always use Makefile commands, NEVER direct tool execution.

### Initial Setup
```bash
make setup      # Complete project setup (installs deps + initializes database)
```

### Development Servers
```bash
make dev           # Start both frontend and backend (smart - checks if already running)
make dev-backend   # Start backend only on http://localhost:8000
make dev-frontend  # Start frontend only on http://localhost:5173
make stop-all      # Stop all development servers
make clean-ports   # Force kill processes on ports 8000 and 5173
```

**IMPORTANT Server Management Rules:**
- ALWAYS check if servers are already running before starting them
- Use `make stop-all` to stop all servers before starting new ones  
- Use `make clean-ports` if ports are stuck
- NEVER start servers directly with `uv run` or `npm run` - ALWAYS use Makefile commands
- NEVER use `npm run dev`, `npm run build`, etc. - ALWAYS use `make dev-frontend`, `make dev-backend`, etc.
- The `make dev` command is smart and checks if servers are already running

### Code Quality & Testing
```bash
make lint          # Run ruff linter on backend code
make format        # Format backend code with ruff (auto-fixes issues)
make typecheck     # Run type checking with mypy
make test          # Run backend tests with pytest
make pr-check      # Run ALL checks before creating a PR

# NEVER run these directly:
# ❌ ruff check src/
# ❌ mypy src/
# ❌ pytest
# ✅ Always use make commands above
```

### Pre-commit Hooks Setup
```bash
# Install pre-commit hooks (run from backend directory)
cd backend && uv run pre-commit install

# Run hooks manually on all files
cd backend && uv run pre-commit run --all-files
```

**CRITICAL**: You are NOT allowed to skip pre-commit hooks (using `--no-verify`) unless explicitly requested. All commits must pass pre-commit checks.

### Database Management
```bash
make db-init       # Initialize SQLite database
make db-clean      # Delete database file (data loss warning!)
```

### Git Workflow
```bash
make branch-new name=<feature-name>  # Create new feature branch with proper naming
make branch-sync                     # Sync current branch with master
```

**Branch Naming Convention:**
- `feat/` - New features
- `fix/` - Bug fixes  
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test updates
- `chore/` - Maintenance tasks

## Performance Considerations

- Use database indexes on frequently queried fields (user_id, currency)
- Implement pagination for account lists
- Use React.memo for expensive components
- Lazy load account details

## Security Best Practices

- JWT tokens for authentication
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection prevention via SQLAlchemy
- XSS prevention in React
- CORS configuration for production

## Common Operations Examples

### Adding a new currency
1. Update currency enum in backend
2. Add currency to frontend types
3. Update exchange rate service
4. Add migration if needed

### Adding a new account field
1. Update SQLAlchemy model
2. Update Pydantic schemas
3. Create and run migration
4. Update frontend types
5. Update UI components
6. Add tests for new field

## Environment Variables

Environment variables are centralized in the project root:
- `.env` file in root directory (ignored by git)
- `.env.example` for reference
- Frontend uses `VITE_` prefix
- Backend uses `JENMONEY_` prefix or reads directly
- Vite config points to parent directory for env files

```env
# Backend
DATABASE_URL=sqlite:///./data/finance.db
SECRET_KEY=your-secret-key
EXCHANGE_RATE_API_KEY=api-key
JENMONEY_DATABASE_URL=sqlite:///./data/finance.db

# Frontend
VITE_API_URL=http://localhost:8000
VITE_REFRESH_INTERVAL=5000
```

## Common Issues and Solutions

1. **Backend ID constraint error**: Ensure `autoincrement=True` on ID columns and recreate DB with `make db-clean && make db-init`

2. **Frontend env variables not loading**: Check that `vite.config.ts` has `envDir: resolve(__dirname, '..')`

3. **Port already in use**: Use `make stop-all` to kill all servers, or `make clean-ports` for force kill

4. **TypeScript errors in vite.config**: Install `@types/node` as dev dependency

5. **Servers already running**: The improved `make dev` command now checks if servers are already running and skips starting them again

6. **Pre-commit hooks not working**: Run `cd backend && uv run pre-commit install` to set up hooks

7. **Python dependencies issues**: Always use `uv add package-name` instead of `pip install`

## Deployment Considerations

- Use production database (PostgreSQL recommended)
- Enable HTTPS
- Set up proper logging
- Configure CORS for production domain
- Use environment-specific configs
- Set up CI/CD pipeline