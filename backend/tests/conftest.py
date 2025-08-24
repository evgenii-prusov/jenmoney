import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from jenmoney.database import Base, get_db
from jenmoney.main import app
from jenmoney import crud, models, schemas

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_accounts(db: Session):
    """Create sample accounts for testing."""
    # Create two accounts
    account_1 = crud.account.create(
        db=db,
        obj_in=schemas.AccountCreate(
            name="Test Account 1",
            currency="EUR",
            balance=1000.00,
            description="First test account"
        )
    )
    
    account_2 = crud.account.create(
        db=db,
        obj_in=schemas.AccountCreate(
            name="Test Account 2", 
            currency="EUR",
            balance=500.00,
            description="Second test account"
        )
    )
    
    return account_1, account_2


@pytest.fixture
def sample_transfers(db: Session, sample_accounts):
    """Create sample transfers for testing."""
    account_1, account_2 = sample_accounts
    
    # Create a few transfers
    transfer_1 = models.Transfer(
        from_account_id=account_1.id,
        to_account_id=account_2.id,
        from_amount=Decimal("100.00"),
        from_currency="EUR",
        to_amount=Decimal("100.00"),
        to_currency="EUR",
        exchange_rate=None,
        description="Test transfer 1",
        status="completed"
    )
    
    transfer_2 = models.Transfer(
        from_account_id=account_2.id,
        to_account_id=account_1.id,
        from_amount=Decimal("50.00"),
        from_currency="EUR", 
        to_amount=Decimal("50.00"),
        to_currency="EUR",
        exchange_rate=None,
        description="Test transfer 2",
        status="completed"
    )
    
    db.add(transfer_1)
    db.add(transfer_2)
    db.commit()
    
    return [transfer_1, transfer_2]
