# Database Migration Note

## Changes Made

### Categories Table Update

The `categories` table has been updated to support hierarchical categories with parent-child relationships.

#### Before
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

#### After
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES categories(id),
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### New Features Added

- **Hierarchical Categories**: Support for parent-child category relationships (2 levels maximum)
- **Parent Category Selection**: When creating/editing categories, you can select a parent category
- **Hierarchical Display**: Categories are displayed in a tree structure in the UI
- **Cascade Deletion**: Deleting a parent category also deletes all its children
- **Validation**: Prevents circular relationships and limits nesting to 2 levels

## Migration Required

If you have existing data in your categories table, you need to run:

```sql
ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id);
CREATE INDEX ix_categories_parent_id ON categories (parent_id);
```

Or recreate the database with:
```bash
make db-clean && make db-init
```

## Example Usage

You can now create hierarchical categories like:

1. **Питание** (Food) - Parent category
   1.1. **Продукты** (Groceries) - Child category
   1.2. **Готовая еда** (Ready food) - Child category  
   1.3. **Рестораны** (Restaurants) - Child category

2. **Транспорт** (Transportation) - Parent category
   2.1. **Общественный транспорт** (Public transport) - Child category
   2.2. **Автомобиль** (Car) - Child category

## API Changes

### New Endpoints
- `GET /api/v1/categories/hierarchy` - Get categories in hierarchical structure
- `GET /api/v1/categories/?hierarchical=true` - Get paginated root categories with children

### Updated Schemas
- **CategoryCreate**: Added optional `parent_id` field
- **CategoryUpdate**: Added optional `parent_id` field  
- **CategoryResponse**: Added `parent_id` and `children` fields

### Validation Rules
- Categories can only have 2 levels (parent → child)
- No circular relationships allowed
- Cannot set a category as its own parent
- Cannot set a child category as parent of its own parent

## Impact

- Existing flat categories continue to work as top-level categories
- New hierarchical functionality is backwards compatible
- Enhanced UI in Settings → Categories shows tree structure
- Better organization for expense/income tracking