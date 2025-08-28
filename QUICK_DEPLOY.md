# Quick Deployment Guide

This guide provides step-by-step instructions for deploying JenMoney to various platforms for production testing.

## 🚀 Platform-Specific Deployment

### 1. DigitalOcean Droplet (Recommended - $6/month)

```bash
# 1. Create a $6/month droplet with Ubuntu 22.04
# 2. SSH into your droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 5. Clone and deploy
git clone https://github.com/evgenii-prusov/jenmoney.git
cd jenmoney

# 6. Configure environment
cp .env.production.example .env.production
nano .env.production  # Edit with your settings

# Required settings:
# DOMAIN=your-droplet-ip
# POSTGRES_PASSWORD=secure-password-123
# SECRET_KEY=$(openssl rand -hex 32)

# 7. Deploy
./deployment/deploy.sh

# 8. Access your app at http://your-droplet-ip
```

### 2. Railway (Easiest - ~$10/month)

```bash
# 1. Fork the repository to your GitHub account
# 2. Go to railway.app and connect your GitHub
# 3. Deploy the repository
# 4. Add environment variables in Railway dashboard:
#    - DATABASE_URL: (Railway will provide PostgreSQL)
#    - JENMONEY_ENVIRONMENT: production
#    - JENMONEY_DEBUG: false
#    - SECRET_KEY: (generate with: openssl rand -hex 32)
# 5. Your app will be available at your Railway URL
```

### 3. AWS EC2 Free Tier

```bash
# 1. Launch Ubuntu 22.04 t2.micro instance
# 2. Configure security group (ports 22, 80, 443)
# 3. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 4. Install Docker (same as DigitalOcean steps 3-4)
# 5. Clone and deploy (same as DigitalOcean steps 5-8)
```

### 4. Google Cloud Platform (Free Tier)

```bash
# 1. Create a new Compute Engine instance (e2-micro)
# 2. Enable HTTP/HTTPS traffic
# 3. SSH into instance (use browser SSH)
# 4. Install Docker and deploy (same as DigitalOcean)
```

## 🔧 Quick Configuration Examples

### Minimal `.env.production`
```env
DOMAIN=134.122.123.45  # Your server IP
VITE_API_URL=http://134.122.123.45/api
POSTGRES_PASSWORD=mySecurePassword123
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef
JENMONEY_ENVIRONMENT=production
JENMONEY_DEBUG=false
```

### With Custom Domain
```env
DOMAIN=jenmoney.yourdomain.com
VITE_API_URL=https://jenmoney.yourdomain.com/api
POSTGRES_PASSWORD=mySecurePassword123
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef
JENMONEY_ENVIRONMENT=production
JENMONEY_DEBUG=false
```

## 🌐 Domain Setup (Optional)

If you have a domain name:

1. **Point domain to your server**:
   - Add A record: `jenmoney.yourdomain.com` → `your-server-ip`

2. **Enable HTTPS** (after deployment):
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Stop nginx temporarily
   docker-compose -f docker-compose.prod.yml stop nginx
   
   # Get certificate
   sudo certbot certonly --standalone -d jenmoney.yourdomain.com
   
   # Copy certificates
   sudo cp /etc/letsencrypt/live/jenmoney.yourdomain.com/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/jenmoney.yourdomain.com/privkey.pem nginx/ssl/
   sudo chown 1000:1000 nginx/ssl/*
   
   # Update nginx config to enable HTTPS block
   nano nginx/conf.d/default.conf  # Uncomment HTTPS server block
   
   # Restart
   docker-compose -f docker-compose.prod.yml up -d
   ```

## 🔍 Testing Your Deployment

After deployment, verify everything works:

```bash
# Check if all services are running
docker-compose -f docker-compose.prod.yml ps

# Check health endpoint
curl http://your-domain/health

# View logs if something's wrong
docker-compose -f docker-compose.prod.yml logs

# Test from another device
# Open http://your-domain in a mobile browser
```

## 📱 Multi-Device Testing

Once deployed, you can access your JenMoney instance from:
- Your phone: `http://your-domain`
- Your tablet: `http://your-domain`
- Other computers: `http://your-domain`
- Work computer: `http://your-domain`

## 💡 Tips for Success

1. **Use your server's IP address** initially, set up domain later
2. **Start simple** - use HTTP first, add HTTPS later
3. **Save your passwords** - write down your PostgreSQL password
4. **Monitor logs** - if something doesn't work, check the logs
5. **Backup your data** - use the database backup commands in the main docs

## 🆘 Common Issues

**Port 80 already in use**: 
```bash
sudo systemctl stop apache2
sudo systemctl stop nginx
```

**Services won't start**:
```bash
docker-compose -f docker-compose.prod.yml logs
```

**Can't access from other devices**:
- Check firewall: `sudo ufw status`
- Enable ports: `sudo ufw allow 80 && sudo ufw allow 443`

**Database connection failed**:
- Check your POSTGRES_PASSWORD in .env.production
- Restart: `docker-compose -f docker-compose.prod.yml restart`

Start with the simplest option for your budget and technical comfort level. DigitalOcean droplet is recommended for the best balance of cost, control, and simplicity.