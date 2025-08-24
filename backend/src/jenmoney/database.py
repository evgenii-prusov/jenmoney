from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from jenmoney.config import settings

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# SQLite specific connection args
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import all models to register them with Base.metadata
    from jenmoney.models import Account, Category, CurrencyRate, Transfer, UserSettings  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Initialize default exchange rates if none exist
    from jenmoney.utils.default_data import initialize_default_exchange_rates

    with SessionLocal() as db:
        initialize_default_exchange_rates(db)
