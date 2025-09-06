#!/bin/bash

# JenMoney Production Deployment Script
# This script helps deploy JenMoney to a VPS or cloud instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 JenMoney Production Deployment${NC}"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}⚠️  .env.production not found. Creating from template...${NC}"
    cp .env.production.example .env.production
    echo -e "${YELLOW}📝 Please edit .env.production with your configuration before continuing.${NC}"
    echo -e "${YELLOW}   Required fields: DOMAIN, POSTGRES_PASSWORD, SECRET_KEY${NC}"
    exit 1
fi

# Source environment variables
source .env.production

# Validate required environment variables
if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "your-domain.com" ]; then
    echo -e "${RED}❌ Please set DOMAIN in .env.production${NC}"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your-secure-password-here" ]; then
    echo -e "${RED}❌ Please set POSTGRES_PASSWORD in .env.production${NC}"
    exit 1
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-very-secure-secret-key-at-least-32-characters-long" ]; then
    echo -e "${RED}❌ Please set SECRET_KEY in .env.production${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment configuration validated${NC}"

# Build and start services
echo -e "${YELLOW}🔨 Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

echo -e "${YELLOW}🚢 Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check if services are healthy
if docker-compose -f docker-compose.prod.yml ps | grep -q "unhealthy\|Exit"; then
    echo -e "${RED}❌ Some services failed to start properly${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo "🌐 Your JenMoney application should be available at:"
echo "   http://$DOMAIN"
echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "🔄 To update the application:"
echo "   git pull && ./deployment/deploy.sh"