# PostgreSQL Migration Guide

JenMoney now supports PostgreSQL as a database backend in addition to the default SQLite. This guide walks you through setting up and migrating to PostgreSQL.

## Why PostgreSQL?

- **Better Performance**: PostgreSQL handles concurrent connections and large datasets more efficiently
- **Production Ready**: More suitable for production deployments
- **Advanced Features**: JSON support, full-text search, and robust transaction handling
- **Scalability**: Better support for multi-user environments

## Setup Options

### Option 1: Using Docker (Recommended)

The easiest way to set up PostgreSQL for development:

```bash
# Start PostgreSQL container
make db-postgres-start

# Check if it's running
make db-postgres-logs

# Initialize the database
DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney make db-init
```

### Option 2: Local PostgreSQL Installation

1. Install PostgreSQL on your system
2. Create database and user:
   ```sql
   CREATE USER jenmoney WITH PASSWORD 'jenmoney';
   CREATE DATABASE jenmoney OWNER jenmoney;
   GRANT ALL PRIVILEGES ON DATABASE jenmoney TO jenmoney;
   ```

## Configuration

### Environment Variables

Update your `.env` file to use PostgreSQL:

```bash
# PostgreSQL configuration
DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney
```

Or use environment variables:
```bash
export JENMONEY_DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney
```

### Connection String Format

```
postgresql://username:password@host:port/database_name
```

Example configurations:
- Local development: `postgresql://jenmoney:jenmoney@localhost:5432/jenmoney`
- Production: `postgresql://user:password@db-server:5432/jenmoney_prod`

## Migration from SQLite

### Step 1: Backup Your SQLite Data

```bash
# Create a backup of your SQLite database
cp backend/data/finance.db backend/data/finance.db.backup
```

### Step 2: Start PostgreSQL

```bash
# Using Docker
make db-postgres-start

# Or use your local PostgreSQL installation
```

### Step 3: Run Migration Script

```bash
# Migrate data from SQLite to PostgreSQL
SQLITE_DATABASE_URL=sqlite:///./data/finance.db \
POSTGRES_DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney \
make db-migrate
```

The migration script will:
- ✅ Extract all data from SQLite database
- ✅ Create all tables in PostgreSQL
- ✅ Migrate all data preserving relationships and IDs
- ✅ Update PostgreSQL sequences for auto-incrementing IDs

### Step 4: Update Configuration

Update your `.env` file to use PostgreSQL:

```bash
DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney
```

### Step 5: Verify Migration

```bash
# Start the application with PostgreSQL
make dev

# Test that everything works correctly
make test
```

## Development Commands

### Database Management

```bash
# Start PostgreSQL container
make db-postgres-start

# Stop PostgreSQL container
make db-postgres-stop

# Remove PostgreSQL container (⚠️ data loss!)
make db-postgres-clean

# View PostgreSQL logs
make db-postgres-logs

# Initialize database (SQLite or PostgreSQL based on DATABASE_URL)
make db-init

# Migrate from SQLite to PostgreSQL
make db-migrate
```

### Testing with PostgreSQL

```bash
# Run tests with PostgreSQL
TEST_DATABASE_URL=postgresql://jenmoney:jenmoney@localhost:5432/jenmoney_test make test

# Default tests still use SQLite in-memory for speed
make test
```

## Troubleshooting

### Connection Issues

**Error**: `connection to server at "localhost", port 5432 failed`

**Solutions**:
1. Ensure PostgreSQL is running: `make db-postgres-logs`
2. Check if port 5432 is available: `lsof -i :5432`
3. Restart the container: `make db-postgres-stop && make db-postgres-start`

### Migration Issues

**Error**: `SQLite database not found`

**Solution**: Ensure the SQLite database path is correct:
```bash
ls -la backend/data/finance.db
```

**Error**: `Target database connection failed`

**Solution**: Verify PostgreSQL is running and accessible:
```bash
psql postgresql://jenmoney:jenmoney@localhost:5432/jenmoney -c "SELECT 1"
```

### Performance Considerations

**Connection Pooling**: For production, consider using connection pooling:
```python
# In production settings
DATABASE_URL=postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=30
```

**Indexes**: The migration preserves all indexes from SQLite. For large datasets, consider adding additional indexes based on your query patterns.

## Production Deployment

### Environment Variables

```bash
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
JENMONEY_DEBUG=false
```

### Security

1. **Use strong passwords** for database user
2. **Enable SSL/TLS** for database connections in production
3. **Restrict database access** to application servers only
4. **Regular backups** using `pg_dump`

### Backup and Restore

```bash
# Backup
pg_dump postgresql://user:pass@host:5432/jenmoney > backup.sql

# Restore
psql postgresql://user:pass@host:5432/jenmoney < backup.sql
```

## Reverting to SQLite

If you need to revert to SQLite:

1. Update `.env`:
   ```bash
   DATABASE_URL=sqlite:///./data/finance.db
   ```

2. Your SQLite backup should still contain your original data:
   ```bash
   cp backend/data/finance.db.backup backend/data/finance.db
   ```

## Next Steps

- Consider setting up automated backups for production
- Monitor database performance and optimize queries as needed
- Set up database monitoring and alerting
- Consider using read replicas for high-traffic applications

For more advanced PostgreSQL configuration, refer to the [PostgreSQL documentation](https://www.postgresql.org/docs/).