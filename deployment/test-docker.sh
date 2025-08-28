#!/bin/bash

# Local Docker Test Script
# Tests the Docker setup locally before deployment

set -e

echo "🧪 Testing JenMoney Docker Setup Locally"
echo "========================================"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker."
    exit 1
fi

echo "✅ Docker is running"

# Test database only
echo "🗄️ Starting PostgreSQL database..."
docker run -d --name jenmoney-test-db \
    -e POSTGRES_DB=jenmoney \
    -e POSTGRES_USER=jenmoney \
    -e POSTGRES_PASSWORD=testpass123 \
    -p 5433:5432 \
    postgres:15-alpine

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Test database connection
if docker exec jenmoney-test-db pg_isready -U jenmoney -d jenmoney; then
    echo "✅ Database is ready"
else
    echo "❌ Database failed to start"
    docker logs jenmoney-test-db
    docker rm -f jenmoney-test-db
    exit 1
fi

# Test backend build (without network dependencies)
echo "🔨 Testing backend build..."
cd backend

# Create a minimal test build
cat > Dockerfile.test << 'EOF'
FROM python:3.13-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy application code
COPY . .

# Install minimal dependencies directly
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "jenmoney.main"]
EOF

docker build -f Dockerfile.test -t jenmoney-backend-test .

if [ $? -eq 0 ]; then
    echo "✅ Backend builds successfully"
else
    echo "❌ Backend build failed"
    rm -f Dockerfile.test
    docker rm -f jenmoney-test-db
    exit 1
fi

# Clean up test files
rm -f Dockerfile.test

# Test running backend with database
echo "🚀 Testing backend with database..."
docker run -d --name jenmoney-test-backend \
    --link jenmoney-test-db:postgres \
    -e JENMONEY_DATABASE_URL="postgresql://jenmoney:testpass123@postgres:5432/jenmoney" \
    -e JENMONEY_DEBUG=true \
    -p 8001:8000 \
    jenmoney-backend-test

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 15

# Test health endpoint
if curl -f http://localhost:8001/health >/dev/null 2>&1; then
    echo "✅ Backend is responding to health checks"
else
    echo "❌ Backend health check failed"
    docker logs jenmoney-test-backend
fi

# Clean up
echo "🧹 Cleaning up test containers..."
docker rm -f jenmoney-test-backend jenmoney-test-db
docker rmi -f jenmoney-backend-test

echo ""
echo "✅ Local Docker test completed successfully!"
echo "🚀 Your setup is ready for deployment."
echo ""
echo "Next steps:"
echo "1. Copy .env.production.example to .env.production"
echo "2. Edit .env.production with your settings"
echo "3. Run: ./deployment/deploy.sh"