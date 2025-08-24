#!/usr/bin/env python3
"""
Minimal FastAPI server to test categories functionality
"""

import sys
import os
from pathlib import Path

# Add the backend src to Python path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

import sqlite3
from datetime import datetime
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    import json
    from typing import List, Optional, Dict, Any
    from pydantic import BaseModel
    
    print("FastAPI available - using full implementation")
    USE_FASTAPI = True
except ImportError:
    print("FastAPI not available - creating minimal test")
    USE_FASTAPI = False

if USE_FASTAPI:
    # Pydantic models
    class CategoryBase(BaseModel):
        name: str
        description: Optional[str] = None
        parent_id: Optional[int] = None
    
    class CategoryCreate(CategoryBase):
        pass
    
    class CategoryResponse(CategoryBase):
        id: int
        created_at: datetime
        updated_at: datetime
        children: List['CategoryResponse'] = []
        
        class Config:
            from_attributes = True
    
    CategoryResponse.model_rebuild()
    
    # Database functions
    def get_db_connection():
        db_path = Path("backend/data/finance.db")
        if not db_path.exists():
            raise HTTPException(status_code=500, detail="Database not found. Run setup_db.py first.")
        return sqlite3.connect(str(db_path))
    
    def get_categories_hierarchy():
        """Get all categories in hierarchical structure"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all categories
        cursor.execute("""
            SELECT id, name, description, parent_id, created_at, updated_at 
            FROM categories 
            ORDER BY parent_id, name
        """)
        rows = cursor.fetchall()
        
        # Create category objects
        categories = {}
        root_categories = []
        
        for row in rows:
            cat = {
                "id": row[0],
                "name": row[1], 
                "description": row[2],
                "parent_id": row[3],
                "created_at": row[4],
                "updated_at": row[5],
                "children": []
            }
            categories[row[0]] = cat
            
            if row[3] is None:  # No parent, it's a root category
                root_categories.append(cat)
        
        # Build hierarchy
        for cat in categories.values():
            if cat["parent_id"] is not None and cat["parent_id"] in categories:
                categories[cat["parent_id"]]["children"].append(cat)
        
        conn.close()
        return root_categories
    
    def create_category(category_data: dict):
        """Create a new category"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Validate parent if provided
        if category_data.get("parent_id"):
            cursor.execute("SELECT id, parent_id FROM categories WHERE id = ?", (category_data["parent_id"],))
            parent = cursor.fetchone()
            if not parent:
                conn.close()
                raise HTTPException(status_code=400, detail="Parent category not found")
            if parent[1] is not None:  # Parent has a parent (grandparent)
                conn.close()
                raise HTTPException(status_code=400, detail="Cannot create more than 2 levels of categories")
        
        # Insert category
        cursor.execute("""
            INSERT INTO categories (name, description, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (category_data["name"], category_data.get("description"), category_data.get("parent_id")))
        
        category_id = cursor.lastrowid
        conn.commit()
        
        # Get the created category
        cursor.execute("""
            SELECT id, name, description, parent_id, created_at, updated_at 
            FROM categories WHERE id = ?
        """, (category_id,))
        row = cursor.fetchone()
        conn.close()
        
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2], 
            "parent_id": row[3],
            "created_at": row[4],
            "updated_at": row[5],
            "children": []
        }
    
    # FastAPI app
    app = FastAPI(title="JenMoney Categories Test")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {"message": "JenMoney Categories Test Server", "database": "connected"}
    
    @app.get("/api/v1/categories/")
    async def read_categories():
        """Get all categories"""
        try:
            categories = get_categories_hierarchy()
            return {
                "items": categories,
                "total": len(categories),
                "page": 1,
                "size": 100,
                "pages": 1
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/categories/hierarchy")
    async def read_categories_hierarchy():
        """Get categories in hierarchical structure"""
        try:
            return get_categories_hierarchy()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/categories/")
    async def create_category_endpoint(category: CategoryCreate):
        """Create a new category"""
        try:
            return create_category(category.dict())
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(status_code=500, detail=str(e))
    
    # Run the server
    if __name__ == "__main__":
        import uvicorn
        print("Starting test server on http://localhost:8000")
        print("Test endpoints:")
        print("  GET http://localhost:8000/api/v1/categories/")
        print("  GET http://localhost:8000/api/v1/categories/hierarchy")
        print("  POST http://localhost:8000/api/v1/categories/")
        uvicorn.run(app, host="0.0.0.0", port=8000)

else:
    # Minimal test without FastAPI
    def test_database():
        """Test database connection and basic operations"""
        db_path = Path("backend/data/finance.db")
        if not db_path.exists():
            print("ERROR: Database not found. Run setup_db.py first.")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test categories table
        try:
            cursor.execute("SELECT COUNT(*) FROM categories")
            count = cursor.fetchone()[0]
            print(f"Categories table: {count} records")
            
            # Test creating a category
            cursor.execute("""
                INSERT INTO categories (name, description, created_at, updated_at)
                VALUES ('Test Category', 'Test Description', datetime('now'), datetime('now'))
            """)
            conn.commit()
            print("Successfully created test category")
            
            # Test reading categories
            cursor.execute("SELECT id, name, description FROM categories")
            categories = cursor.fetchall()
            print("Categories:")
            for cat in categories:
                print(f"  {cat[0]}: {cat[1]} - {cat[2] or 'No description'}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Database test failed: {e}")
            conn.close()
            return False
    
    if __name__ == "__main__":
        print("Testing database functionality...")
        test_database()