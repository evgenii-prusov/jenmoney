# JenMoney Production Deployment Guide

This guide explains how to deploy JenMoney for production use, allowing you to access it from multiple devices for testing and real-world usage.

## 🏗️ Architecture Overview

The production deployment uses:
- **Frontend**: React app served by Nginx
- **Backend**: FastAPI application with PostgreSQL database
- **Database**: PostgreSQL for production-grade data persistence
- **Reverse Proxy**: Nginx for routing and SSL termination
- **Containerization**: Docker and Docker Compose for easy deployment

## 🚀 Quick Start

### Prerequisites

1. **Server**: A VPS or cloud instance (minimum 1GB RAM, 10GB storage)
2. **Docker**: Install Docker and Docker Compose on your server
3. **Domain** (optional): A domain name pointing to your server's IP
4. **Git**: To clone the repository

### 1. Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group (optional, to avoid sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 2. Deploy JenMoney

```bash
# Clone the repository
git clone https://github.com/evgenii-prusov/jenmoney.git
cd jenmoney

# Copy and edit environment configuration
cp .env.production.example .env.production
nano .env.production  # Edit with your settings

# Run deployment script
./deployment/deploy.sh
```

### 3. Environment Configuration

Edit `.env.production` with your settings:

```env
# Your domain (or IP address)
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api

# Secure database password
POSTGRES_PASSWORD=your-very-secure-password

# Backend security key (generate with: openssl rand -hex 32)
SECRET_KEY=your-32-character-secret-key
```

## 🌐 Deployment Options

### Option 1: VPS with Domain (Recommended)

**Providers**: DigitalOcean, Linode, Vultr, AWS EC2

1. **Purchase a VPS** (1GB RAM minimum)
2. **Configure domain DNS** to point to your server IP
3. **Follow Quick Start** above
4. **Setup SSL** (see SSL Setup section)

**Cost**: ~$5-10/month

### Option 2: Cloud Platform (Easiest)

**Providers**: Railway, Render, Heroku

1. **Fork the repository** to your GitHub account
2. **Connect your repository** to the platform
3. **Configure environment variables** in the platform dashboard
4. **Deploy** using the platform's interface

**Cost**: ~$10-20/month (with database)

### Option 3: Local Network (Testing)

For testing on your local network only:

```bash
# Use development Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# Access at http://your-local-ip:3000
```

## 🔒 SSL/HTTPS Setup (Production)

### Using Let's Encrypt (Free)

1. **Install Certbot**:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. **Stop Nginx temporarily**:
```bash
docker-compose -f docker-compose.prod.yml stop nginx
```

3. **Generate certificate**:
```bash
sudo certbot certonly --standalone -d your-domain.com
```

4. **Update nginx configuration** to enable HTTPS:
```bash
# Edit nginx/conf.d/default.conf
# Uncomment the HTTPS server block and update domain
```

5. **Copy certificates to nginx directory**:
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
sudo chown 1000:1000 nginx/ssl/*
```

6. **Restart services**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Database Management
```bash
# Backup database
docker exec -t jenmoney_postgres_1 pg_dump -U jenmoney jenmoney > backup.sql

# Restore database
docker exec -i jenmoney_postgres_1 psql -U jenmoney jenmoney < backup.sql

# Access database shell
docker exec -it jenmoney_postgres_1 psql -U jenmoney jenmoney
```

### Updates
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

### Stop Services
```bash
# Stop all services
docker-compose -f docker-compose.prod.yml down

# Stop and remove volumes (⚠️ deletes data)
docker-compose -f docker-compose.prod.yml down -v
```

## 🔍 Troubleshooting

### Services Won't Start
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# View specific service logs
docker-compose -f docker-compose.prod.yml logs backend
```

### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Verify database connectivity
docker exec jenmoney_backend_1 pg_isready -h postgres -U jenmoney
```

### Frontend Not Loading
```bash
# Check Nginx logs
docker-compose -f docker-compose.prod.yml logs nginx

# Verify frontend build
docker-compose -f docker-compose.prod.yml logs frontend
```

### Port Already in Use
```bash
# Find what's using the port
sudo lsof -i :80
sudo lsof -i :443

# Stop conflicting services
sudo systemctl stop apache2  # If Apache is running
sudo systemctl stop nginx    # If system Nginx is running
```

## 🔐 Security Considerations

1. **Change default passwords** in `.env.production`
2. **Use strong SECRET_KEY** (generate with `openssl rand -hex 32`)
3. **Enable firewall**:
   ```bash
   sudo ufw enable
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   ```
4. **Keep system updated**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Regular backups** of database and configuration

## 📊 Monitoring

### Health Checks
```bash
# Check application health
curl http://your-domain.com/health

# Check all services
docker-compose -f docker-compose.prod.yml ps
```

### Performance Monitoring
```bash
# View resource usage
docker stats

# Database performance
docker exec jenmoney_postgres_1 psql -U jenmoney -c "SELECT * FROM pg_stat_activity;"
```

## 🆘 Support

If you encounter issues:

1. **Check logs** first: `docker-compose -f docker-compose.prod.yml logs`
2. **Verify environment** configuration in `.env.production`
3. **Check firewall** settings and port accessibility
4. **Review this documentation** for common solutions

For additional help, check the main project documentation or create an issue in the GitHub repository.

## 📝 Next Steps

After successful deployment:

1. **Access your application** at your domain/IP
2. **Create your first account** and add some test transactions
3. **Test from multiple devices** to verify remote access
4. **Set up regular backups** for your data
5. **Consider monitoring** setup for production use

Enjoy using JenMoney in production! 🎉