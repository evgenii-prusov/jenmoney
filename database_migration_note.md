# Database Migration Note

## Changes Made

The `status` column has been removed from the `transfers` table as requested in the PR review.

### Before
```sql
CREATE TABLE transfers (
    ...
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    ...
);
```

### After
```sql
CREATE TABLE transfers (
    ...
    -- status column removed
    ...
);
```

## Migration Required

If you have existing data in your transfers table, you may need to run:

```sql
ALTER TABLE transfers DROP COLUMN status;
```

Or recreate the database with:
```bash
make db-clean && make db-init
```

## Impact

- All transfers are now considered "completed" by default when created
- No status tracking or status updates are supported
- Simpler transfer workflow as requested