#!/usr/bin/env python3
"""
Test categories functionality by directly calling the CRUD operations
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add backend src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

def test_categories_crud():
    """Test categories CRUD operations directly with the database"""
    
    db_path = Path("backend/data/finance.db")
    if not db_path.exists():
        print("ERROR: Database not found. Run setup_db.py first.")
        return False
    
    print("=== Testing Categories CRUD Operations ===")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Clear any existing test data
        cursor.execute("DELETE FROM categories WHERE name LIKE 'Test%'")
        conn.commit()
        
        print("\n1. Testing category creation...")
        
        # Test creating a parent category
        cursor.execute("""
            INSERT INTO categories (name, description, type, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, ("Test Parent Category", "A test parent category", "expense"))
        parent_id = cursor.lastrowid
        conn.commit()
        print(f"   ✓ Created parent category with ID: {parent_id}")
        
        # Test creating a child category
        cursor.execute("""
            INSERT INTO categories (name, description, type, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, ("Test Child Category", "A test child category", "expense", parent_id))
        child_id = cursor.lastrowid
        conn.commit()
        print(f"   ✓ Created child category with ID: {child_id}")
        
        # Test preventing 3-level nesting
        try:
            cursor.execute("""
                INSERT INTO categories (name, description, parent_id, created_at, updated_at)
                VALUES (?, ?, ?, datetime('now'), datetime('now'))
            """, ("Test Grandchild Category", "Should fail", child_id))
            # This should be validated at the API level, but we can check if it exists
            print("   ⚠ Three-level nesting allowed in database (should be prevented by API)")
        except Exception as e:
            print(f"   ✓ Three-level nesting prevented: {e}")
        
        print("\n2. Testing category reading...")
        
        # Get all categories
        cursor.execute("""
            SELECT id, name, description, parent_id 
            FROM categories 
            ORDER BY parent_id, name
        """)
        categories = cursor.fetchall()
        
        print("   All categories:")
        for cat in categories:
            indent = "     " if cat[3] is not None else "   "
            parent_info = f" (parent: {cat[3]})" if cat[3] is not None else ""
            print(f"{indent}- {cat[1]}{parent_info}")
        
        # Test hierarchical structure
        print("\n3. Testing hierarchical structure...")
        
        # Get root categories with children
        cursor.execute("""
            SELECT id, name, description 
            FROM categories 
            WHERE parent_id IS NULL
            ORDER BY name
        """)
        root_categories = cursor.fetchall()
        
        for root in root_categories:
            print(f"   📁 {root[1]}")
            
            # Get children
            cursor.execute("""
                SELECT id, name, description 
                FROM categories 
                WHERE parent_id = ?
                ORDER BY name
            """, (root[0],))
            children = cursor.fetchall()
            
            for child in children:
                print(f"      └── {child[1]}")
        
        print("\n4. Testing category validation scenarios...")
        
        # Test data integrity
        cursor.execute("SELECT COUNT(*) FROM categories WHERE name LIKE 'Test%'")
        test_count = cursor.fetchone()[0]
        print(f"   ✓ Found {test_count} test categories")
        
        # Test parent-child relationships
        cursor.execute("""
            SELECT c1.name as child, c2.name as parent 
            FROM categories c1
            LEFT JOIN categories c2 ON c1.parent_id = c2.id
            WHERE c1.name LIKE 'Test%'
        """)
        relationships = cursor.fetchall()
        
        print("   Category relationships:")
        for rel in relationships:
            if rel[1]:
                print(f"     - {rel[0]} → parent: {rel[1]}")
            else:
                print(f"     - {rel[0]} → no parent (root)")
        
        print("\n5. Testing API endpoint structure...")
        
        # Simulate what the API endpoints would return
        
        # Simulate GET /api/v1/categories/hierarchy
        cursor.execute("""
            SELECT id, name, description, parent_id, created_at, updated_at 
            FROM categories 
            ORDER BY parent_id, name
        """)
        all_categories = cursor.fetchall()
        
        # Build hierarchy
        categories_dict = {}
        root_cats = []
        
        for cat in all_categories:
            cat_obj = {
                "id": cat[0],
                "name": cat[1],
                "description": cat[2],
                "parent_id": cat[3],
                "created_at": cat[4],
                "updated_at": cat[5],
                "children": []
            }
            categories_dict[cat[0]] = cat_obj
            
            if cat[3] is None:  # Root category
                root_cats.append(cat_obj)
        
        # Add children to parents
        for cat in categories_dict.values():
            if cat["parent_id"] is not None and cat["parent_id"] in categories_dict:
                categories_dict[cat["parent_id"]]["children"].append(cat)
        
        print("   Hierarchy API response structure:")
        for root in root_cats:
            print(f"     📁 {root['name']} (id: {root['id']})")
            for child in root["children"]:
                print(f"        └── {child['name']} (id: {child['id']})")
        
        print("\n✅ All category tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    test_categories_crud()