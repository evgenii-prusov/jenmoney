# Quick Setup Instructions

If you're getting category loading errors, follow these steps:

## 1. Initialize Database
```bash
cd /path/to/jenmoney
python3 setup_db.py
```

This will create:
- `backend/data/finance.db` with all required tables
- Categories table with hierarchical support (parent_id field)
- Sample currency exchange rates
- Default user settings

## 2. Start the Application

### If you have UV installed:
```bash
make setup
make dev
```

### If UV is not available:
You'll need to install the required Python packages:
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-multipart
```

Then start manually:
```bash
cd backend
PYTHONPATH=src python3 -m jenmoney.main
```

## 3. Test Categories

Once the server is running, you can test:
- Visit http://localhost:8000/api/v1/categories/
- Visit http://localhost:8000/api/v1/categories/hierarchy
- Use the frontend at http://localhost:5173

## 4. Verify Setup

Run the test script to verify everything works:
```bash
python3 test_categories.py
```

## Database Structure

The categories table now supports:
- **Hierarchical relationships**: parent_id field for 2-level nesting
- **Validation**: Prevents circular references and >2 levels
- **Cascade deletion**: Deleting parent removes children
- **Example structure**:
  ```
  📁 Питание (Food)
     └── Продукты (Groceries)
     └── Рестораны (Restaurants)
  📁 Транспорт (Transportation)  
     └── Автомобиль (Car)
  ```

## Frontend Features

- Parent category selection dropdown
- Visual tree structure with indentation
- Create/edit forms with validation
- Settings → Categories tab shows hierarchy

The hierarchical categories feature is now fully functional!