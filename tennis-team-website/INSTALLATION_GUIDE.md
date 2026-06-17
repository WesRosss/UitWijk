# Tennis Team Website - Installation Guide

## 📋 Overview

This guide explains how to install the Tennis Team Website on your **Debian server with existing Apache2** as a reverse proxy.

### Architecture
```
Internet → Apache2 (Host Machine) → Docker Containers
                                    ├── Backend (Django) :8000
                                    ├── Frontend (Vue.js) :8080
                                    ├── Database (PostgreSQL) :5432
                                    ├── Redis :6379
                                    └── Celery Services
```

## 🚀 Step 1: Clone the Project

```bash
# SSH into your server
ssh your-username@your-server-ip

# Clone the repository
git clone https://github.com/WesRosss/UitWijk.git
cd UitWijk/tennis-team-website
```

## 🐳 Step 2: Install Docker and Docker Compose

```bash
# Update package lists
sudo apt update

# Install Docker
sudo apt install -y docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to avoid using sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker-compose --version
```

## ⚙️ Step 3: Configure Apache2 as Reverse Proxy

### 3.1 Enable Required Apache2 Modules

```bash
# Enable proxy modules
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod proxy_wstunnel
sudo a2enmod rewrite
sudo a2enmod headers

# Optional: For HTTPS
sudo a2enmod ssl
```

### 3.2 Copy and Configure Apache2 Configuration

```bash
# Copy the provided configuration
sudo cp apache-proxy.conf /etc/apache2/sites-available/tennis-team.conf

# Edit the configuration to match your domain
sudo nano /etc/apache2/sites-available/tennis-team.conf

# Replace these values:
# - ServerName: Change to your domain (e.g., tennis.yourdomain.com)
# - ServerAdmin: Change to your email
# - ProxyPass targets: Keep as 127.0.0.1:8000 and 127.0.0.1:8080

# Enable the site
sudo a2ensite tennis-team.conf

# Disable default site (optional)
sudo a2dissite 000-default.conf

# Test configuration
sudo apache2ctl configtest

# Restart Apache2
sudo systemctl restart apache2
```

### 3.3 HTTPS Configuration (Recommended for Production)

```bash
# Install Certbot for Let's Encrypt
sudo apt install -y certbot python3-certbot-apache

# Obtain SSL certificate
sudo certbot --apache -d tennis.yourdomain.com

# Certbot will automatically modify your Apache configuration
# Follow the prompts to complete the setup

# Test HTTPS
sudo apache2ctl configtest
sudo systemctl restart apache2
```

## 📦 Step 4: Configure and Start Docker Containers

### 4.1 Set Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env

# Important: Set a strong secret key
# Generate one with: python -c "import secrets; print(secrets.token_urlsafe(50))"
DJANGO_SECRET_KEY=your-generated-secret-key-here

# For development, you can use these defaults:
# DATABASE_URL=postgres://tennis_user:tennis_password@database:5432/tennis_db
# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### 4.2 Build and Start Containers

```bash
# Build the containers (this may take several minutes)
docker-compose build

# Start all services
docker-compose up -d

# Check if all containers are running
docker-compose ps
```

### 4.3 Wait for Initialization

```bash
# View logs to check initialization progress
docker-compose logs -f

# Wait until you see:
# - database: database system is ready to accept connections
# - backend: Started server
# - frontend: Compiled successfully

# Press Ctrl+C to exit log viewing
```

## 🔧 Step 5: Run Database Migrations

```bash
# Run Django migrations
docker-compose exec backend python manage.py migrate

# Create superuser (optional)
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput
```

## 🌐 Step 6: Access the Application

### Development Mode (with Vue.js dev server)
- **Frontend**: http://your-server-ip/
- **Backend API**: http://your-server-ip/api/
- **Admin**: http://your-server-ip/admin/

### Production Mode (recommended)
For production, you should build the frontend and serve it through Django:

```bash
# Build frontend
docker-compose exec frontend npm run build

# The built files will be in frontend/dist
# You can configure Django to serve these files
```

## 📋 Step 7: Default Credentials

The database initialization script creates these users:
- **Admin**: username: `admin`, password: `admin123`
- **Coordinator**: username: `coordinator`, password: `admin123`
- **Player**: username: `player1`, password: `admin123`

## 🔄 Common Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend

# Restart specific service
docker-compose restart backend

# Run database migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Build frontend
docker-compose exec frontend npm run build

# Run management commands
docker-compose exec backend python manage.py <command>
```

## 🛡️ Security Configuration

### Change Default Credentials

```bash
# Change admin password
docker-compose exec backend python manage.py shell

# In the Django shell:
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='admin')
user.set_password('new-strong-password')
user.save()
exit()
```

### Generate New Secret Key

```bash
# Generate a new secret key
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Update .env file with the new key
nano .env
```

## 📊 Monitoring and Maintenance

### Check Container Status

```bash
# List running containers
docker-compose ps

# View resource usage
docker stats

# Check disk usage
docker system df
```

### Cleanup

```bash
# Remove stopped containers, unused networks, and dangling images
docker system prune

# Remove all unused containers, networks, images (both dangling and unreferenced)
docker system prune -a
```

## 🔄 Updates

### Pull Latest Changes

```bash
# Pull latest code from repository
cd /path/to/tennis-team-website
git pull origin main

# Rebuild containers
docker-compose build

# Restart services
docker-compose up -d --force-recreate

# Run migrations if database schema changed
docker-compose exec backend python manage.py migrate
```

## 🚨 Troubleshooting

### Apache2 Proxy Issues

**Problem**: 502 Bad Gateway

**Solution**:
```bash
# Check if containers are running
docker-compose ps

# Check Apache2 error logs
sudo tail -f /var/log/apache2/error.log

# Check if ports are exposed correctly
netstat -tulnp | grep -E '8000|8080'
```

### Database Connection Issues

**Problem**: Database connection refused

**Solution**:
```bash
# Check if database container is healthy
docker-compose ps

# View database logs
docker-compose logs database

# Test database connection manually
docker-compose exec backend python manage.py check --database default
```

### Frontend Not Loading

**Problem**: Blank page or loading errors

**Solution**:
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose exec frontend npm run build

# Check if Vue.js dev server is running
docker-compose ps | grep frontend
```

### Permission Issues

**Problem**: Permission denied errors

**Solution**:
```bash
# Set correct permissions on volumes
sudo chown -R $USER:$USER backend/ frontend/ docker/

# Restart containers
docker-compose restart
```

## 📝 Apache2 Configuration Notes

### For Development
The provided `apache-proxy.conf` proxies:
- `/api/*` → Django backend on port 8000
- `/admin/*` → Django admin on port 8000
- `/static/*` → Django static files on port 8000
- `/media/*` → Django media files on port 8000
- `/` → Vue.js frontend on port 8080
- `/ws/*` → WebSocket connections to backend

### For Production
For production, you should:
1. Build the frontend: `docker-compose exec frontend npm run build`
2. Configure Django to serve the built frontend files
3. Update Apache2 to proxy `/` to Django instead of Vue.js dev server
4. Or serve the built files directly from Apache2

### Example Production Apache2 Configuration

```apache
<VirtualHost *:80>
    ServerName tennis.yourdomain.com
    
    # Serve built frontend files
    DocumentRoot /path/to/tennis-team-website/frontend/dist
    
    <Directory /path/to/tennis-team-website/frontend/dist>
        Require all granted
        Options -Indexes
    </Directory>
    
    # Proxy API requests to Django
    ProxyPass /api http://127.0.0.1:8000/api
    ProxyPassReverse /api http://127.0.0.1:8000/api
    
    ProxyPass /admin http://127.0.0.1:8000/admin
    ProxyPassReverse /admin http://127.0.0.1:8000/admin
    
    ProxyPass /static http://127.0.0.1:8000/static
    ProxyPassReverse /static http://127.0.0.1:8000/static
    
    ProxyPass /media http://127.0.0.1:8000/media
    ProxyPassReverse /media http://127.0.0.1:8000/media
    
    # WebSocket support
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} =websocket [NC]
    RewriteCond %{HTTP:Connection} =upgrade [NC]
    RewriteRule /ws/(.*) ws://127.0.0.1:8000/ws/$1 [P,L]
</VirtualHost>
```

## 🎯 Final Checklist

- [ ] Docker and Docker Compose installed
- [ ] Apache2 installed and running
- [ ] Apache2 proxy modules enabled
- [ ] Apache2 configuration copied and enabled
- [ ] Project cloned and environment configured
- [ ] Docker containers built and running
- [ ] Database migrations executed
- [ ] Static files collected
- [ ] Application accessible via browser

## 📞 Support

If you encounter any issues:
1. Check the logs: `docker-compose logs -f`
2. Verify Apache2 configuration: `sudo apache2ctl configtest`
3. Check container status: `docker-compose ps`
4. Review this installation guide

For additional help, refer to the main [README.md](README.md) file.