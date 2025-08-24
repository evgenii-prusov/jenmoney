#!/usr/bin/env python3
"""
Simple database initialization script for JenMoney
Creates the required database tables without needing full dependencies
"""

import sqlite3
import os
from pathlib import Path

def create_tables():
    """Create all required tables for JenMoney"""
    
    # Ensure data directory exists
    data_dir = Path("backend/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Database file path
    db_path = data_dir / "finance.db"
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Check if categories table exists and get its structure
    cursor.execute("PRAGMA table_info(categories)")
    existing_columns = {col[1]: col[2] for col in cursor.fetchall()}
    
    if not existing_columns:
        # Create categories table with hierarchical support and type
        cursor.execute("""
            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                type VARCHAR(10) NOT NULL DEFAULT 'expense',
                parent_id INTEGER REFERENCES categories(id),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Created new categories table with type support")
    else:
        # Check if type column exists, if not add it
        if 'type' not in existing_columns:
            print("Adding type column to existing categories table...")
            cursor.execute("""
                ALTER TABLE categories 
                ADD COLUMN type VARCHAR(10) NOT NULL DEFAULT 'expense'
            """)
            print("Added type column with default value 'expense'")
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_parent_id ON categories (parent_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_name ON categories (name)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_type ON categories (type)
    """)
    
    # Create accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
            currency VARCHAR(3) NOT NULL DEFAULT 'USD',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create user_settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            default_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create currency_rates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            currency_from VARCHAR(3) NOT NULL,
            currency_to VARCHAR(3) NOT NULL DEFAULT 'USD',
            rate DECIMAL(15,6) NOT NULL,
            effective_from DATETIME NOT NULL,
            effective_to DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create transfers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_account_id INTEGER NOT NULL REFERENCES accounts(id),
            to_account_id INTEGER NOT NULL REFERENCES accounts(id),
            amount DECIMAL(15,2) NOT NULL,
            description TEXT,
            transfer_date DATE NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'completed',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default user settings
    cursor.execute("""
        INSERT OR IGNORE INTO user_settings (id, default_currency) 
        VALUES (1, 'USD')
    """)
    
    # Insert some basic exchange rates
    cursor.execute("""
        INSERT OR IGNORE INTO currency_rates (currency_from, currency_to, rate, effective_from)
        VALUES 
            ('EUR', 'USD', 1.1, datetime('now')),
            ('USD', 'EUR', 0.91, datetime('now')),
            ('RUB', 'USD', 0.011, datetime('now')),
            ('USD', 'RUB', 91.0, datetime('now')),
            ('JPY', 'USD', 0.0067, datetime('now')),
            ('USD', 'JPY', 149.0, datetime('now'))
    """)
    
    # Commit changes
    conn.commit()
    
    # Verify tables were created
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"Database created at: {db_path}")
    print("Created tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Test category table structure
    cursor.execute("PRAGMA table_info(categories)")
    columns = cursor.fetchall()
    print("\nCategories table structure:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    return db_path

if __name__ == "__main__":
    create_tables()