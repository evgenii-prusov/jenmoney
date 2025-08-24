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
    
    # Create categories table with hierarchical support
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            parent_id INTEGER REFERENCES categories(id),
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on parent_id for performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_parent_id ON categories (parent_id)
    """)
    
    # Create index on name for performance  
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_categories_name ON categories (name)
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
            key VARCHAR(100) NOT NULL UNIQUE,
            value TEXT,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create currency_rates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS currency_rates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_currency VARCHAR(3) NOT NULL,
            to_currency VARCHAR(3) NOT NULL,
            rate DECIMAL(15,6) NOT NULL,
            effective_date DATE NOT NULL,
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
        INSERT OR IGNORE INTO user_settings (key, value) 
        VALUES ('default_currency', 'USD')
    """)
    
    # Insert some basic exchange rates
    cursor.execute("""
        INSERT OR IGNORE INTO currency_rates (from_currency, to_currency, rate, effective_date)
        VALUES 
            ('EUR', 'USD', 1.1, date('now')),
            ('USD', 'EUR', 0.91, date('now')),
            ('RUB', 'USD', 0.011, date('now')),
            ('USD', 'RUB', 91.0, date('now')),
            ('JPY', 'USD', 0.0067, date('now')),
            ('USD', 'JPY', 149.0, date('now'))
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