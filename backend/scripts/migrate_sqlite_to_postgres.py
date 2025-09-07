#!/usr/bin/env python3
"""
Migration script to move data from SQLite to PostgreSQL.

This script:
1. Connects to the existing SQLite database
2. Extracts all data from SQLite tables
3. Connects to PostgreSQL database
4. Creates all tables in PostgreSQL
5. Migrates all data preserving relationships and IDs

Usage:
    python scripts/migrate_sqlite_to_postgres.py

Environment variables:
    SQLITE_DATABASE_URL: Source SQLite database URL (default: sqlite:///./data/finance.db)
    POSTGRES_DATABASE_URL: Target PostgreSQL database URL (default: postgresql://jenmoney:jenmoney@localhost:5432/jenmoney)
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from decimal import Decimal
from datetime import datetime

# Add backend src to path
backend_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(backend_src))

import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from jenmoney.database import Base
from jenmoney.models import Account, Budget, Category, CurrencyRate, Transaction, Transfer, UserSettings


def get_sqlite_data(sqlite_url: str) -> Dict[str, List[Dict[str, Any]]]:
    """Extract all data from SQLite database."""
    
    if sqlite_url.startswith("sqlite:///"):
        sqlite_path = sqlite_url.replace("sqlite:///", "")
    else:
        sqlite_path = sqlite_url.replace("sqlite://", "")
    
    if not Path(sqlite_path).exists():
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")
    
    print(f"🔍 Reading data from SQLite: {sqlite_path}")
    
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    cursor = conn.cursor()
    
    data = {}
    
    # Define tables to migrate in dependency order
    tables = [
        "user_settings",
        "currency_rates", 
        "accounts",
        "categories",
        "budgets",
        "transactions",
        "transfers"
    ]
    
    for table in tables:
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]
            print(f"  📊 {table}: {len(rows)} records")
        except sqlite3.OperationalError as e:
            if "no such table" in str(e):
                print(f"  ⚠️  Table {table} does not exist, skipping")
                data[table] = []
            else:
                raise
    
    conn.close()
    return data


def migrate_to_postgres(postgres_url: str, data: Dict[str, List[Dict[str, Any]]]) -> None:
    """Migrate data to PostgreSQL database."""
    
    print(f"🔗 Connecting to PostgreSQL: {postgres_url}")
    
    # Create PostgreSQL engine
    engine = create_engine(postgres_url, echo=False)
    
    # Create all tables
    print("🏗️  Creating PostgreSQL tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # Clear existing data (in dependency order)
        print("🧹 Clearing existing data...")
        session.execute(text("TRUNCATE TABLE transfers CASCADE"))
        session.execute(text("TRUNCATE TABLE transactions CASCADE"))
        session.execute(text("TRUNCATE TABLE budgets CASCADE"))
        session.execute(text("TRUNCATE TABLE categories CASCADE"))
        session.execute(text("TRUNCATE TABLE accounts CASCADE"))
        session.execute(text("TRUNCATE TABLE currency_rates CASCADE"))
        session.execute(text("TRUNCATE TABLE user_settings CASCADE"))
        session.commit()
        
        # Migrate data
        print("📦 Migrating data...")
        
        # 1. User Settings
        if data.get("user_settings"):
            for row in data["user_settings"]:
                user_setting = UserSettings(
                    id=row["id"],
                    default_currency=row["default_currency"],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(user_setting)
            print(f"  ✅ Migrated {len(data['user_settings'])} user settings")
        
        # 2. Currency Rates
        if data.get("currency_rates"):
            for row in data["currency_rates"]:
                currency_rate = CurrencyRate(
                    id=row["id"],
                    currency_from=row["currency_from"],
                    currency_to=row["currency_to"],
                    rate=Decimal(str(row["rate"])),
                    effective_from=datetime.fromisoformat(row["effective_from"]),
                    effective_to=datetime.fromisoformat(row["effective_to"]) if row["effective_to"] else None,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(currency_rate)
            print(f"  ✅ Migrated {len(data['currency_rates'])} currency rates")
        
        # 3. Accounts
        if data.get("accounts"):
            for row in data["accounts"]:
                account = Account(
                    id=row["id"],
                    name=row["name"],
                    currency=row["currency"],
                    balance=Decimal(str(row["balance"])),
                    description=row.get("description"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(account)
            print(f"  ✅ Migrated {len(data['accounts'])} accounts")
        
        # 4. Categories
        if data.get("categories"):
            for row in data["categories"]:
                category = Category(
                    id=row["id"],
                    name=row["name"],
                    description=row.get("description"),
                    parent_id=row.get("parent_id"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(category)
            print(f"  ✅ Migrated {len(data['categories'])} categories")
        
        # 5. Budgets
        if data.get("budgets"):
            for row in data["budgets"]:
                budget = Budget(
                    id=row["id"],
                    name=row["name"],
                    category_id=row.get("category_id"),
                    amount=Decimal(str(row["amount"])),
                    period=row["period"],
                    start_date=datetime.fromisoformat(row["start_date"]).date() if row["start_date"] else None,
                    end_date=datetime.fromisoformat(row["end_date"]).date() if row["end_date"] else None,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(budget)
            print(f"  ✅ Migrated {len(data['budgets'])} budgets")
        
        # 6. Transactions
        if data.get("transactions"):
            for row in data["transactions"]:
                transaction = Transaction(
                    id=row["id"],
                    account_id=row["account_id"],
                    category_id=row.get("category_id"),
                    amount=Decimal(str(row["amount"])),
                    description=row.get("description"),
                    transaction_date=datetime.fromisoformat(row["transaction_date"]).date() if row["transaction_date"] else None,
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(transaction)
            print(f"  ✅ Migrated {len(data['transactions'])} transactions")
        
        # 7. Transfers
        if data.get("transfers"):
            for row in data["transfers"]:
                transfer = Transfer(
                    id=row["id"],
                    from_account_id=row["from_account_id"],
                    to_account_id=row["to_account_id"],
                    from_amount=Decimal(str(row["from_amount"])),
                    from_currency=row["from_currency"],
                    to_amount=Decimal(str(row["to_amount"])),
                    to_currency=row["to_currency"],
                    exchange_rate=Decimal(str(row["exchange_rate"])) if row.get("exchange_rate") else None,
                    description=row.get("description"),
                    transfer_date=datetime.fromisoformat(row["transfer_date"]).date() if row["transfer_date"] else None,
                    status=row.get("status", "completed"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.utcnow(),
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else datetime.utcnow()
                )
                session.add(transfer)
            print(f"  ✅ Migrated {len(data['transfers'])} transfers")
        
        session.commit()
        
        # Update sequences for auto-incrementing IDs
        print("🔢 Updating PostgreSQL sequences...")
        tables_with_ids = ["user_settings", "currency_rates", "accounts", "categories", "budgets", "transactions", "transfers"]
        
        for table in tables_with_ids:
            if data.get(table):
                max_id = max((row["id"] for row in data[table]), default=0)
                if max_id > 0:
                    session.execute(text(f"SELECT setval('{table}_id_seq', {max_id}, true)"))
        
        session.commit()
        
        print("🎉 Migration completed successfully!")


def main():
    """Main migration function."""
    
    # Get database URLs from environment or use defaults
    sqlite_url = os.getenv("SQLITE_DATABASE_URL", "sqlite:///./data/finance.db")
    postgres_url = os.getenv("POSTGRES_DATABASE_URL", "postgresql://jenmoney:jenmoney@localhost:5432/jenmoney")
    
    print("🚀 Starting SQLite to PostgreSQL migration")
    print(f"📂 Source: {sqlite_url}")
    print(f"🐘 Target: {postgres_url}")
    print()
    
    try:
        # Extract data from SQLite
        data = get_sqlite_data(sqlite_url)
        
        # Migrate to PostgreSQL
        migrate_to_postgres(postgres_url, data)
        
        print()
        print("✨ Migration completed successfully!")
        print("💡 Don't forget to update your DATABASE_URL environment variable to use PostgreSQL")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()