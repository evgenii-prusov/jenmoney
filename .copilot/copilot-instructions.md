# Jenmoney - Personal Finance Management Application

This is a personal finance application for tracking multiple currency accounts with real-time exchange rate conversion. Built as a Single Page Application (SPA) with React + Material UI frontend and FastAPI backend.

## Architecture Overview

```
jenmoney/
├── backend/          # FastAPI backend
│   ├── src/         # Source code
│   │   ├── api/     # API endpoints (versioned)
│   │   ├── models/  # SQLAlchemy models
│   │   ├── schemas/ # Pydantic schemas
│   │   └── services/# Business logic
│   └── tests/       # Pytest tests
├── frontend/        # React + Vite frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/      # Custom React hooks
│   │   ├── api/        # API client (TanStack Query)
│   │   └── types/      # TypeScript types
│   └── tests/
└── Makefile        # Common operations
```

## Core Features & User Flow

1. **Account Management**: Users can create, edit, delete, and view multiple currency accounts
2. **Multi-currency Support**: Each account has a native currency; amounts are displayed in both native and default currency
3. **Real-time Updates**: TanStack Query with 5-second auto-refresh for live currency conversion
4. **Total Balance**: Header displays aggregate balance in user's default currency

## Tech Stack & Dependencies

### Backend (Python 3.13+)
- **Framework**: FastAPI with async support
- **Database**: SQLite with SQLAlchemy ORM
- **Validation**: Pydantic v2
- **Package Manager**: uv
- **Testing**: pytest with pytest-asyncio
- **Linting**: ruff (configured in pyproject.toml)

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

### TypeScript/React
- Functional components with TypeScript
- Custom hooks for shared logic
- Interfaces over types for object shapes
- Descriptive component names: `AccountListHeader` not `Header`

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

```bash
# Start development servers
make dev          # Starts both frontend and backend

# Run tests
make test         # Runs all tests
make test-backend # Backend tests only
make test-frontend # Frontend tests only

# Static analysis
make lint         # Runs ruff for Python, ESLint for TypeScript
make format       # Auto-formats code

# Database operations
make db-migrate   # Apply migrations
make db-reset     # Reset database
```

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

```env
# Backend
DATABASE_URL=sqlite:///./jenmoney.db
SECRET_KEY=your-secret-key
EXCHANGE_RATE_API_KEY=api-key

# Frontend
VITE_API_URL=http://localhost:8000
VITE_REFRESH_INTERVAL=5000
```

## Deployment Considerations

- Use production database (PostgreSQL recommended)
- Enable HTTPS
- Set up proper logging
- Configure CORS for production domain
- Use environment-specific configs
- Set up CI/CD pipeline