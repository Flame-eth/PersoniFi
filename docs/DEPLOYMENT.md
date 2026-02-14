# PersoniFi Deployment Guide

## Overview

This guide covers deploying PersoniFi to production using Docker, PostgreSQL, Redis, and Nginx. The deployment architecture supports horizontal scaling with load balancing.

## Prerequisites

- Docker and Docker Compose installed
- AWS account (for cloud deployment) or VPS access
- Domain name configured
- SSL certificate (Let's Encrypt recommended)
- GitHub Actions secrets configured

## Local Development with Docker

### Starting the Application

1. Clone the repository:

```bash
git clone https://github.com/your-repo/PersoniFi.git
cd PersoniFi
```

2. Create environment file:

```bash
cp .env.production.example .env
# Edit .env with local settings
```

3. Build and start services:

```bash
docker-compose up -d
```

4. Create superuser:

```bash
docker-compose exec web python manage.py createsuperuser
```

5. Access the application:

- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- GraphQL: http://localhost:8000/graphql

### Stopping Services

```bash
docker-compose down
```

### Viewing Logs

```bash
# View all services
docker-compose logs -f

# View specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

## Production Deployment on AWS

### 1. Setup EC2 Instance

```bash
# Launch EC2 instance (Ubuntu 20.04 LTS recommended)
# Instance type: t3.medium or larger
# Security Groups: Allow ports 80, 443, 22

# SSH into instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/your-repo/PersoniFi.git
sudo chown -R $USER:$USER PersoniFi
cd PersoniFi
```

### 3. Configure Environment

```bash
# Copy production environment template
cp .env.production.example .env

# Edit with production values
nano .env
# Set:
# - DEBUG=False
# - SECRET_KEY (generate secure key)
# - ALLOWED_HOSTS
# - DATABASE_URL
# - REDIS_URL
# - Email configuration
# - AWS credentials (if using S3)
```

### 4. Start Services

```bash
# Start all services in background
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 5. Configure SSL Certificate

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx.conf with certificate paths
sudo nano nginx.conf

# Uncomment HTTPS block and update paths:
# ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

# Mount certificates in docker-compose.yml
docker-compose down
docker-compose up -d
```

### 6. Setup Auto-renewal for SSL

```bash
# Create renewal script
sudo nano /etc/cron.d/certbot-renewal

# Add:
# 0 */12 * * * /usr/bin/certbot renew --quiet

sudo systemctl restart cron
```

## Performance Optimization

### Database Optimization

```bash
# Connect to PostgreSQL
docker-compose exec db psql -U personifi -d personifi

# Create indexes
CREATE INDEX idx_transaction_user ON transactions(user_id);
CREATE INDEX idx_transaction_date ON transactions(date);
CREATE INDEX idx_account_user ON accounts(user_id);

# Check query performance
EXPLAIN ANALYZE SELECT * FROM transactions WHERE user_id = 'user-id';
```

### Redis Caching

The application automatically uses Redis for:

- Session management
- Query caching
- Celery task queue

### Nginx Performance

Nginx configuration includes:

- Gzip compression
- Static file caching
- Connection pooling
- Worker processes optimized for CPU cores

## Monitoring and Maintenance

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health/

# Check database
docker-compose exec db pg_isready

# Check Redis
docker-compose exec redis redis-cli ping
redis::6379> PONG
```

### Backup Strategy

```bash
# Backup database
docker-compose exec db pg_dump -U personifi personifi > backup.sql

# Backup media files
tar -czf media_backup.tar.gz media/

# Restore database
docker-compose exec -T db psql -U personifi personifi < backup.sql
```

### Update and Maintenance

```bash
# Pull latest code
git pull origin main

# Rebuild Docker image
docker-compose down
docker build -t personifi:latest .
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Verify application
curl http://localhost:8000/health/
```

## Scaling the Application

### Horizontal Scaling

1. Add more web instances behind load balancer
2. Use managed PostgreSQL (AWS RDS)
3. Use managed Redis (AWS ElastiCache)

### Load Balancing

```yaml
# Use AWS Application Load Balancer (ALB)
# - Target group: EC2 instances running PersoniFi
# - Health check: /health/
# - Stickiness: Enable if needed
```

### Database Connection Pooling

```bash
# Use PgBouncer for connection pooling
# Configuration:
# - Pool size: 20 connections per worker
# - Reserve pool: 5 connections
# - Max DB connections: 200
```

## Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check database connectivity
docker-compose exec web python manage.py dbshell

# Check connection string
echo $DATABASE_URL
```

#### Static Files Not Loading

```bash
# Collect and verify static files
docker-compose exec web python manage.py collectstatic --noinput -c

# Check file permissions
docker-compose exec web ls -la staticfiles/
```

#### Redis Connection Issues

```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Flush Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

#### Slow Queries

```bash
# Enable query logging in PostgreSQL
docker-compose exec db psql -U personifi -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"
docker-compose restart db

# Review slow query log
docker-compose logs -f db | grep duration
```

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable SSL/TLS
- [ ] Set up CORS properly
- [ ] Configure email for notifications
- [ ] Set strong database passwords
- [ ] Enable database backups
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts
- [ ] Regular security updates
- [ ] Rotate access keys periodically

## Monitoring with Third-Party Services

### Sentry Error Tracking

```bash
# Set SENTRY_DSN in environment
SENTRY_DSN=https://key@sentry.io/project-id
```

### DataDog or New Relic

```bash
# Install monitoring agent
docker-compose exec web pip install datadog

# Configure environment variables
DD_AGENT_HOST=datadog-agent
DD_AGENT_PORT=8126
```

## Disaster Recovery

### Database Disaster Recovery

```bash
# Regular backup schedule
0 2 * * * /usr/local/bin/backup-db.sh

# Test restore procedure monthly
./restore-db.sh test_backup.sql
```

### Application Disaster Recovery

```bash
# Keep multiple regions/availability zones
# Use AWS RDS Multi-AZ for database
# Use S3 for media backups
```

## Performance Benchmarking

### Run Benchmarks

```bash
# Run pytest benchmarks
pytest tests/performance/benchmarks.py -v --benchmark-only

# Run load tests with Locust
locust -f tests/performance/locustfile.py --host=https://your-domain.com
```

### Expected Performance Metrics

- API response time: < 200ms (p95)
- Database queries: < 100ms (p95)
- Static asset delivery: < 50ms
- GraphQL query: < 300ms (p95)

## Getting Help

- Documentation: See DEPLOYMENT_RUNBOOK.md
- Issue Tracker: GitHub Issues
- Community: Discord/Slack channel
