# AIxWord - Deployment Guide

**Version:** 1.0.0  
**Last Updated:** September 29, 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Reverse Proxy Setup](#reverse-proxy-setup)
7. [SSL/TLS Configuration](#ssltls-configuration)
8. [Monitoring & Logging](#monitoring--logging)
9. [Security Hardening](#security-hardening)
10. [Performance Optimization](#performance-optimization)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)
13. [Maintenance](#maintenance)

---

## Introduction

This guide provides comprehensive instructions for deploying the AIxWord application to production environments. It covers both traditional server deployment and containerized deployment options.

### Deployment Options

**Option 1: Traditional Server Deployment**
- Direct deployment on Ubuntu/Debian/CentOS servers
- Systemd service management
- Nginx reverse proxy
- Suitable for: Single server deployments, VPS hosting

**Option 2: Docker Deployment**
- Containerized deployment with Docker
- Docker Compose orchestration
- Suitable for: Multi-container setups, cloud platforms

**Option 3: Cloud Platform Deployment**
- Platform-specific deployment (AWS, GCP, Azure, Heroku)
- Managed services integration
- Suitable for: Scalable production deployments

### Architecture Overview

```
                                    ┌─────────────────┐
                                    │   Internet      │
                                    └────────┬────────┘
                                             │
                                    ┌────────▼────────┐
                                    │  Load Balancer  │
                                    │   (Optional)    │
                                    └────────┬────────┘
                                             │
                        ┌────────────────────┴────────────────────┐
                        │                                         │
                ┌───────▼────────┐                       ┌───────▼────────┐
                │  Nginx (443)   │                       │  Nginx (443)   │
                │  Reverse Proxy │                       │  Reverse Proxy │
                └───────┬────────┘                       └───────┬────────┘
                        │                                         │
        ┌───────────────┴───────────────┐                        │
        │                               │                        │
┌───────▼────────┐            ┌────────▼────────┐      ┌────────▼────────┐
│  Frontend      │            │  Backend API    │      │  Backend API    │
│  (Static)      │            │  (Port 8000)    │      │  (Port 8001)    │
│  React App     │            │  FastAPI        │      │  FastAPI        │
└────────────────┘            └─────────────────┘      └─────────────────┘
```

---

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk**: 20GB SSD
- **OS**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+

**Recommended Requirements:**
- **CPU**: 4 cores
- **RAM**: 8GB
- **Disk**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS

### Required Software

**Backend:**
- Python 3.11+
- pip
- virtualenv
- systemd (for service management)

**Frontend:**
- Node.js 18+
- npm

**Infrastructure:**
- Nginx or Apache
- Certbot (for SSL)
- Git

**Optional:**
- Docker & Docker Compose
- PostgreSQL (for future database integration)
- Redis (for caching)
- Prometheus & Grafana (for monitoring)

### External Services

**Required:**
- OpenAI API account with valid API key
- Domain name (for production)
- SSL certificate (Let's Encrypt recommended)

**Optional:**
- CDN service (Cloudflare, AWS CloudFront)
- Email service (SendGrid, AWS SES)
- Monitoring service (Datadog, New Relic)

### Installation Commands

**Ubuntu/Debian:**
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Nginx
sudo apt-get install -y nginx

# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Install Git
sudo apt-get install -y git

# Verify installations
python3.11 --version
node --version
nginx -v
certbot --version
```

**CentOS/RHEL:**
```bash
# Update system
sudo yum update -y

# Install Python 3.11
sudo yum install -y python311 python311-pip

# Install Node.js 18
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Install Nginx
sudo yum install -y nginx

# Install Certbot
sudo yum install -y certbot python3-certbot-nginx

# Install Git
sudo yum install -y git
```

---

## Environment Configuration

### Production Environment Variables

#### Backend Environment (.env.production)

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-prod-your-production-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
OPENAI_TIMEOUT=60

# Grid Configuration
DEFAULT_GRID_SIZE=8
MAX_ITERATIONS=50
MIN_FILL_RATE=0.6
MAX_WORDS_PER_PUZZLE=20

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=production
DEBUG=false

# CORS Configuration
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]

# Security
SECRET_KEY=your-secret-key-change-this-to-random-string
ALLOWED_HOSTS=["yourdomain.com","www.yourdomain.com"]
SECURE_COOKIES=true
CSRF_PROTECTION=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_PER_DAY=10000

# Performance
WORKERS=4
WORKER_TIMEOUT=120
KEEPALIVE=5
MAX_REQUESTS=1000
MAX_REQUESTS_JITTER=50

# Logging
LOG_FILE=/var/log/aixword/backend.log
LOG_MAX_SIZE=10485760  # 10MB
LOG_BACKUP_COUNT=5
LOG_FORMAT=json

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

#### Frontend Environment (.env.production)

```bash
# API Configuration
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_API_TIMEOUT=60000

# Environment
VITE_ENVIRONMENT=production
VITE_DEBUG=false

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_REPORTING=true

# Analytics (Optional)
VITE_GA_TRACKING_ID=UA-XXXXXXXXX-X
VITE_SENTRY_DSN=your-sentry-dsn

# Performance
VITE_ENABLE_PWA=true
VITE_CACHE_STRATEGY=cache-first
```

### Security Best Practices

**1. API Key Management:**
```bash
# Never commit .env files
echo ".env" >> .gitignore
echo ".env.production" >> .gitignore

# Use environment-specific files
.env.development
.env.staging
.env.production

# Restrict file permissions
chmod 600 .env.production
```

**2. Secret Generation:**
```bash
# Generate secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate random password
openssl rand -base64 32
```

**3. Environment Variable Loading:**
```python
# backend/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str
    secret_key: str
    environment: str = "production"
    
    class Config:
        env_file = ".env.production"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## Backend Deployment

### Option 1: Traditional Server Deployment

#### Step 1: Clone Repository

```bash
# Create application directory
sudo mkdir -p /opt/aixword
sudo chown $USER:$USER /opt/aixword

# Clone repository
cd /opt
git clone https://github.com/yourusername/AIxWord.git
cd AIxWord/backend
```

#### Step 2: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install application
pip install -e .

# Install production server
pip install gunicorn uvicorn[standard]
```

#### Step 3: Configure Environment

```bash
# Copy production environment file
cp .env.example .env.production

# Edit environment file
nano .env.production

# Set proper permissions
chmod 600 .env.production
```

#### Step 4: Create Systemd Service

**Create service file:**
```bash
sudo nano /etc/systemd/system/aixword-backend.service
```

**Service configuration:**
```ini
[Unit]
Description=AIxWord Backend API
After=network.target
Wants=network-online.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/AIxWord/backend
Environment="PATH=/opt/AIxWord/backend/venv/bin"
Environment="PYTHONPATH=/opt/AIxWord/backend"

# Load environment variables
EnvironmentFile=/opt/AIxWord/backend/.env.production

# Start command
ExecStart=/opt/AIxWord/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/log/aixword/access.log \
    --error-logfile /var/log/aixword/error.log \
    --log-level info \
    backend.main:app

# Restart policy
Restart=always
RestartSec=10
StartLimitInterval=0

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/aixword

[Install]
WantedBy=multi-user.target
```

#### Step 5: Setup Logging

```bash
# Create log directory
sudo mkdir -p /var/log/aixword
sudo chown www-data:www-data /var/log/aixword
sudo chmod 755 /var/log/aixword

# Create log rotation configuration
sudo nano /etc/logrotate.d/aixword
```

**Log rotation configuration:**
```
/var/log/aixword/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload aixword-backend > /dev/null 2>&1 || true
    endscript
}
```

#### Step 6: Set Permissions

```bash
# Set ownership
sudo chown -R www-data:www-data /opt/AIxWord

# Set directory permissions
sudo find /opt/AIxWord -type d -exec chmod 755 {} \;

# Set file permissions
sudo find /opt/AIxWord -type f -exec chmod 644 {} \;

# Make scripts executable
sudo chmod +x /opt/AIxWord/backend/run_server.py
```

#### Step 7: Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable aixword-backend

# Start service
sudo systemctl start aixword-backend

# Check status
sudo systemctl status aixword-backend

# View logs
sudo journalctl -u aixword-backend -f
```

#### Step 8: Verify Backend

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}

# Test API documentation
curl http://localhost:8000/docs
```

### Option 2: Docker Deployment

#### Step 1: Create Dockerfile

**Backend Dockerfile:**
```dockerfile
# backend/Dockerfile

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml setup.py ./
COPY backend/ ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir gunicorn uvicorn[standard]

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "backend.main:app"]
```

#### Step 2: Create Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: aixword-backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    env_file:
      - backend/.env.production
    volumes:
      - ./logs:/var/log/aixword
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - aixword-network

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: aixword-frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - aixword-network

  nginx:
    image: nginx:alpine
    container_name: aixword-nginx
    ports:
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - aixword-network

networks:
  aixword-network:
    driver: bridge

volumes:
  logs:
```

#### Step 3: Build and Deploy

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

---

## Frontend Deployment

### Option 1: Static Hosting with Nginx

#### Step 1: Build Production Bundle

```bash
cd frontend

# Install dependencies
npm ci --production

# Build for production
npm run build

# Output will be in dist/ directory
ls -la dist/
```

#### Step 2: Deploy to Server

```bash
# Create web directory
sudo mkdir -p /var/www/aixword

# Copy build files
sudo cp -r dist/* /var/www/aixword/

# Set ownership
sudo chown -R www-data:www-data /var/www/aixword

# Set permissions
sudo find /var/www/aixword -type d -exec chmod 755 {} \;
sudo find /var/www/aixword -type f -exec chmod 644 {} \;
```

#### Step 3: Verify Deployment

```bash
# List files
ls -la /var/www/aixword/

# Expected structure:
# index.html
# assets/
# favicon.ico
```

### Option 2: Docker Deployment

**Frontend Dockerfile:**
```dockerfile
# frontend/Dockerfile

# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Nginx configuration for frontend:**
```nginx
# frontend/nginx.conf

server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### Option 3: CDN Deployment

#### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
cd frontend
vercel --prod
```

**vercel.json:**
```json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://api.yourdomain.com/api/$1"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

#### Netlify Deployment

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd frontend
netlify deploy --prod
```

**netlify.toml:**
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/api/*"
  to = "https://api.yourdomain.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    X-XSS-Protection = "1; mode=block"
```

---

## Reverse Proxy Setup

### Nginx Configuration

**Create site configuration:**
```bash
sudo nano /etc/nginx/sites-available/aixword
```

**Configuration:**
```nginx
# Backend API upstream
upstream backend_api {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    # Add more backend servers for load balancing
    # server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';" always;

    # Frontend static files
    root /var/www/aixword;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json
               image/svg+xml;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
        
        # Cache control for HTML
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend_api;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $server_name;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        
        # Cache bypass
        proxy_cache_bypass $http_upgrade;
        
        # Error handling
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_next_upstream_tries 2;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Deny access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

**Enable site:**
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/aixword /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## SSL/TLS Configuration

### Let's Encrypt with Certbot

#### Step 1: Install Certbot

```bash
# Ubuntu/Debian
sudo apt-get install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

#### Step 2: Obtain Certificate

```bash
# Obtain certificate for domain
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms of service
# - Choose whether to redirect HTTP to HTTPS (recommended: yes)
```

#### Step 3: Verify Certificate

```bash
# Check certificate
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run
```

#### Step 4: Auto-Renewal

```bash
# Certbot automatically sets up renewal
# Verify cron job or systemd timer
sudo systemctl status certbot.timer

# Manual renewal (if needed)
sudo certbot renew
```

### Custom SSL Certificate

If using a custom SSL certificate:

```bash
# Copy certificate files
sudo cp your-certificate.crt /etc/nginx/ssl/
sudo cp your-private-key.key /etc/nginx/ssl/
sudo cp your-ca-bundle.crt /etc/nginx/ssl/

# Set permissions
sudo chmod 644 /etc/nginx/ssl/your-certificate.crt
sudo chmod 600 /etc/nginx/ssl/your-private-key.key
sudo chmod 644 /etc/nginx/ssl/your-ca-bundle.crt

# Update Nginx configuration
ssl_certificate /etc/nginx/ssl/your-certificate.crt;
ssl_certificate_key /etc/nginx/ssl/your-private-key.key;
ssl_trusted_certificate /etc/nginx/ssl/your-ca-bundle.crt;
```

---

## Monitoring & Logging

### Application Monitoring

#### Health Checks

**Backend Health Endpoint:**
```python
# backend/api/routes.py

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Monitoring Script:**
```bash
#!/bin/bash
# /usr/local/bin/check-aixword-health.sh

BACKEND_URL="http://localhost:8000/health"
FRONTEND_URL="http://localhost/health"

# Check backend
if curl -f -s "$BACKEND_URL" > /dev/null; then
    echo "Backend: OK"
else
    echo "Backend: FAILED"
    systemctl restart aixword-backend
fi

# Check frontend
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "Frontend: OK"
else
    echo "Frontend: FAILED"
    systemctl reload nginx
fi
```

**Setup Cron Job:**
```bash
# Add to crontab
crontab -e

# Check every 5 minutes
*/5 * * * * /usr/local/bin/check-aixword-health.sh >> /var/log/aixword/health-check.log 2>&1
```

### Logging Configuration

#### Centralized Logging

**Configure rsyslog:**
```bash
# /etc/rsyslog.d/aixword.conf

# AIxWord backend logs
if $programname == 'aixword-backend' then /var/log/aixword/backend.log
& stop

# AIxWord access logs
if $programname == 'nginx' and $msg contains 'aixword' then /var/log/aixword/access.log
& stop
```

**Restart rsyslog:**
```bash
sudo systemctl restart rsyslog
```

#### Log Aggregation (Optional)

**Using ELK Stack:**

1. **Install Filebeat:**
```bash
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.x.x-amd64.deb
sudo dpkg -i filebeat-8.x.x-amd64.deb
```

2. **Configure Filebeat:**
```yaml
# /etc/filebeat/filebeat.yml

filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/aixword/*.log
  fields:
    app: aixword
    environment: production

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "aixword-%{+yyyy.MM.dd}"
```

3. **Start Filebeat:**
```bash
sudo systemctl enable filebeat
sudo systemctl start filebeat
```

### Performance Monitoring

#### Prometheus Integration

**Install Prometheus:**
```bash
# Download Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.x.x/prometheus-2.x.x.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Create service
sudo cp prometheus /usr/local/bin/
sudo cp promtool /usr/local/bin/
```

**Configure Prometheus:**
```yaml
# /etc/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'aixword-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

**Add Metrics to Backend:**
```python
# backend/main.py

from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
request_count = Counter('aixword_requests_total', 'Total requests')
request_duration = Histogram('aixword_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard

**Install Grafana:**
```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

**Access Grafana:**
- URL: http://localhost:3000
- Default credentials: admin/admin

---

## Security Hardening

### Firewall Configuration

**UFW (Ubuntu):**
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow backend (if needed)
# sudo ufw allow 8000/tcp

# Check status
sudo ufw status
```

**firewalld (CentOS):**
```bash
# Start firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow services
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh

# Reload
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

### Fail2Ban Configuration

**Install Fail2Ban:**
```bash
sudo apt-get install fail2ban
```

**Configure Fail2Ban:**
```bash
# /etc/fail2ban/jail.local

[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
```

**Start Fail2Ban:**
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### API Rate Limiting

**Backend Rate Limiting:**
```python
# backend/api/middleware.py

from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Apply rate limits
    return await call_next(request)
```

**Nginx Rate Limiting:**
```nginx
# /etc/nginx/nginx.conf

http {
    # Rate limiting zone
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            # ... other config
        }
    }
}
```

---

## Performance Optimization

### Backend Optimization

**1. Worker Configuration:**
```bash
# Calculate optimal workers
# workers = (2 * CPU_cores) + 1

# For 4 CPU cores:
--workers 9
```

**2. Connection Pooling:**
```python
# backend/config.py

# Database connection pool (future)
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
SQLALCHEMY_POOL_RECYCLE = 3600
```

**3. Caching (Redis):**
```python
# backend/cache.py

from redis import Redis
from functools import wraps

redis_client = Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Frontend Optimization

**1. Code Splitting:**
```typescript
// frontend/src/App.tsx

import { lazy, Suspense } from 'react';

const PuzzleGenerator = lazy(() => import('./components/PuzzleGenerator'));
const CrosswordGrid = lazy(() => import('./components/CrosswordGrid'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/generate" element={<PuzzleGenerator />} />
        <Route path="/solve" element={<CrosswordGrid />} />
      </Routes>
    </Suspense>
  );
}
```

**2. Asset Optimization:**
```bash
# Optimize images
npm install -D vite-plugin-imagemin

# vite.config.ts
import viteImagemin from 'vite-plugin-imagemin';

export default {
  plugins: [
    viteImagemin({
      gifsicle: { optimizationLevel: 7 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      svgo: { plugins: [{ removeViewBox: false }] }
    })
  ]
};
```

**3. CDN Integration:**
```html
<!-- index.html -->
<link rel="preconnect" href="https://cdn.yourdomain.com">
<link rel="dns-prefetch" href="https://cdn.yourdomain.com">
```

### Database Optimization (Future)

When database is added:

**1. Indexing:**
```sql
CREATE INDEX idx_puzzle_topic ON puzzles(topic);
CREATE INDEX idx_puzzle_created ON puzzles(created_at);
CREATE INDEX idx_word_placement ON word_placements(puzzle_id, word);
```

**2. Query Optimization:**
```python
# Use select_related and prefetch_related
puzzles = Puzzle.objects.select_related('user').prefetch_related('words')
```

**3. Connection Pooling:**
```python
# Use connection pooling
DATABASE_URL = "postgresql://user:pass@localhost/db?pool_size=20&max_overflow=40"
```

---

## Backup & Recovery

### Backup Strategy

**1. Application Code:**
```bash
#!/bin/bash
# /usr/local/bin/backup-aixword-code.sh

BACKUP_DIR="/var/backups/aixword"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup application code
tar -czf "$BACKUP_DIR/aixword-code-$DATE.tar.gz" \
    -C /opt AIxWord \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git'

# Keep only last 7 days
find "$BACKUP_DIR" -name "aixword-code-*.tar.gz" -mtime +7 -delete
```

**2. Configuration Files:**
```bash
#!/bin/bash
# /usr/local/bin/backup-aixword-config.sh

BACKUP_DIR="/var/backups/aixword"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup configuration
tar -czf "$BACKUP_DIR/aixword-config-$DATE.tar.gz" \
    /opt/AIxWord/backend/.env.production \
    /opt/AIxWord/frontend/.env.production \
    /etc/nginx/sites-available/aixword \
    /etc/systemd/system/aixword-backend.service
```

**3. Database Backup (Future):**
```bash
#!/bin/bash
# /usr/local/bin/backup-aixword-db.sh

BACKUP_DIR="/var/backups/aixword"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="aixword"

# Backup database
pg_dump -U postgres "$DB_NAME" | gzip > "$BACKUP_DIR/aixword-db-$DATE.sql.gz"

# Keep only last 30 days
find "$BACKUP_DIR" -name "aixword-db-*.sql.gz" -mtime +30 -delete
```

**4. Setup Cron Jobs:**
```bash
# Add to crontab
crontab -e

# Daily code backup at 2 AM
0 2 * * * /usr/local/bin/backup-aixword-code.sh

# Daily config backup at 2:15 AM
15 2 * * * /usr/local/bin/backup-aixword-config.sh

# Daily database backup at 2:30 AM (future)
30 2 * * * /usr/local/bin/backup-aixword-db.sh
```

### Recovery Procedures

**1. Restore Application:**
```bash
# Stop services
sudo systemctl stop aixword-backend
sudo systemctl stop nginx

# Restore code
cd /opt
sudo tar -xzf /var/backups/aixword/aixword-code-YYYYMMDD_HHMMSS.tar.gz

# Restore configuration
sudo tar -xzf /var/backups/aixword/aixword-config-YYYYMMDD_HHMMSS.tar.gz -C /

# Reinstall dependencies
cd /opt/AIxWord/backend
source venv/bin/activate
pip install -e .

cd /opt/AIxWord/frontend
npm install

# Start services
sudo systemctl start aixword-backend
sudo systemctl start nginx
```

**2. Restore Database (Future):**
```bash
# Restore database
gunzip < /var/backups/aixword/aixword-db-YYYYMMDD_HHMMSS.sql.gz | psql -U postgres aixword
```

---

## Troubleshooting

### Common Issues

**Issue 1: Backend Won't Start**

**Symptoms:**
- Service fails to start
- 502 Bad Gateway errors

**Diagnosis:**
```bash
# Check service status
sudo systemctl status aixword-backend

# View logs
sudo journalctl -u aixword-backend -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

**Solutions:**
```bash
# Check environment variables
cat /opt/AIxWord/backend/.env.production

# Check Python environment
source /opt/AIxWord/backend/venv/bin/activate
python -c "import backend; print(backend.__version__)"

# Check permissions
ls -la /opt/AIxWord/backend

# Restart service
sudo systemctl restart aixword-backend
```

**Issue 2: High Memory Usage**

**Symptoms:**
- Server running out of memory
- OOM killer terminating processes

**Diagnosis:**
```bash
# Check memory usage
free -h
top -o %MEM

# Check process memory
ps aux --sort=-%mem | head -10
```

**Solutions:**
```bash
# Reduce worker count
# Edit /etc/systemd/system/aixword-backend.service
--workers 2  # Instead of 4

# Add memory limits
# Add to service file:
MemoryLimit=2G
MemoryMax=2.5G

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart aixword-backend
```

**Issue 3: SSL Certificate Errors**

**Symptoms:**
- Certificate expired warnings
- HTTPS not working

**Diagnosis:**
```bash
# Check certificate
sudo certbot certificates

# Test SSL
openssl s_client -connect yourdomain.com:443
```

**Solutions:**
```bash
# Renew certificate
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal

# Reload Nginx
sudo systemctl reload nginx
```

**Issue 4: Slow Response Times**

**Symptoms:**
- API requests taking too long
- Timeouts

**Diagnosis:**
```bash
# Check backend logs
sudo journalctl -u aixword-backend -f

# Monitor requests
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health

# Check system resources
htop
```

**Solutions:**
```bash
# Increase worker timeout
# Edit service file:
--timeout 180  # Instead of 120

# Enable caching (Redis)
# Add Redis caching layer

# Optimize database queries (future)
# Add indexes, use query optimization
```

---

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor logs for errors
- Check service status
- Review resource usage

**Weekly:**
- Review security logs
- Check backup integrity
- Update dependencies (if needed)

**Monthly:**
- Review and rotate logs
- Update SSL certificates (if needed)
- Performance optimization review
- Security audit

**Quarterly:**
- System updates
- Dependency updates
- Security patches
- Performance testing

### Update Procedures

**1. Backend Updates:**
```bash
# Backup current version
/usr/local/bin/backup-aixword-code.sh

# Pull latest code
cd /opt/AIxWord
git pull origin main

# Update dependencies
cd backend
source venv/bin/activate
pip install --upgrade -e .

# Run tests
pytest

# Restart service
sudo systemctl restart aixword-backend

# Verify
curl http://localhost:8000/health
```

**2. Frontend Updates:**
```bash
# Pull latest code
cd /opt/AIxWord/frontend

# Update dependencies
npm install

# Build
npm run build

# Deploy
sudo cp -r dist/* /var/www/aixword/

# Reload Nginx
sudo systemctl reload nginx

# Verify
curl http://localhost/health
```

**3. System Updates:**
```bash
# Update system packages
sudo apt-get update
sudo apt-get upgrade -y

# Update security patches
sudo apt-get dist-upgrade -y

# Reboot if kernel updated
sudo reboot
```

### Monitoring Checklist

**Daily Checks:**
- [ ] Backend service running
- [ ] Frontend accessible
- [ ] No errors in logs
- [ ] SSL certificate valid
- [ ] Disk space available
- [ ] Memory usage normal
- [ ] CPU usage normal

**Weekly Checks:**
- [ ] Backup integrity
- [ ] Log rotation working
- [ ] Security updates available
- [ ] Performance metrics normal
- [ ] Rate limiting working
- [ ] Health checks passing

**Monthly Checks:**
- [ ] SSL certificate expiry (>30 days)
- [ ] Dependency updates available
- [ ] Security audit passed
- [ ] Performance optimization needed
- [ ] Capacity planning review

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying AIxWord to production environments. Follow the steps carefully and adapt them to your specific infrastructure requirements.

### Key Takeaways

1. **Security First**: Always use HTTPS, keep secrets secure, and follow security best practices
2. **Monitor Everything**: Set up comprehensive monitoring and logging
3. **Automate Backups**: Regular automated backups are essential
4. **Test Thoroughly**: Test deployments in staging before production
5. **Document Changes**: Keep deployment documentation up to date

### Support

For deployment issues or questions:
- Review this guide thoroughly
- Check application logs
- Consult the troubleshooting section
- Review related documentation

---

**Version:** 1.0.0  
**Last Updated:** September 29, 2026  
**Maintained By:** AIxWord Development Team

---

*For additional documentation, see the [Documentation Index](../DOCUMENTATION_INDEX.md)*
