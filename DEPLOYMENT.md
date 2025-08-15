# 🚀 Deployment Guide - AI-Powered Risk & Scenario Advisor

This guide covers deploying the application in production environments with security, scalability, and monitoring considerations.

## 📋 Prerequisites

- Python 3.10+
- Redis (for rate limiting)
- PostgreSQL (recommended for production)
- SSL certificate
- Domain name
- Google Gemini API key

## 🏗️ Production Architecture

```
┌─────────────────┐    HTTPS/SSL    ┌──────────────────┐
│                 │ ◄─────────────► │                  │
│   Load Balancer │                 │   FastAPI        │
│   (Nginx)       │                 │   Backend        │
└─────────────────┘                 └──────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│                 │                 │                  │
│   Streamlit     │                 │   PostgreSQL     │
│   Frontend      │                 │   Database       │
└─────────────────┘                 └──────────────────┘
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌──────────────────┐
│                 │                 │                  │
│   Redis         │                 │   Monitoring     │
│   (Rate Limiting)│                 │   (Prometheus)   │
└─────────────────┘                 └──────────────────┘
```

## 🔧 Environment Configuration

### 1. Production Environment Variables

Create a production `.env` file:

```bash
# Production Environment Variables
API_BASE_URL=https://your-domain.com/api
SECRET_KEY=your-super-secure-production-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Gemini AI API
GEMINI_API_KEY=your-production-gemini-api-key

# Database Configuration (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/investment_advisor

# Security Settings
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
ENABLE_HTTPS=true
DEBUG_MODE=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=500

# Logging
LOG_LEVEL=WARNING
LOG_FILE=/var/log/investment_advisor/app.log

# Redis
REDIS_URL=redis://localhost:6379

# Export Settings
MAX_EXPORT_SIZE_MB=5
EXPORT_RETENTION_DAYS=7
```

### 2. Security Considerations

#### JWT Secret Key
Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Database Security
- Use strong passwords
- Enable SSL connections
- Restrict database access
- Regular backups

#### API Security
- Enable HTTPS only
- Implement proper CORS
- Use rate limiting
- Monitor for suspicious activity

## 🐳 Docker Deployment

### 1. Create Dockerfile

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY run_backend.py .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "run_backend.py"]
```

### 2. Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/investment_advisor
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=investment_advisor
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🌐 Nginx Configuration

### 1. Nginx Config

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:8501;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }
    }
}
```

## 📊 Monitoring & Logging

### 1. Application Monitoring

```python
# Add to backend/main.py
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### 2. Log Aggregation

```python
# Structured logging
import structlog

logger = structlog.get_logger()
logger.info("user_action", user_id=user.id, action="portfolio_analysis")
```

### 3. Health Checks

```python
@app.get("/health")
async def health_check():
    # Check database connection
    try:
        session = next(get_session())
        session.exec("SELECT 1").first()
    except Exception:
        return {"status": "unhealthy", "database": "down"}
    
    # Check Redis connection
    try:
        redis_client.ping()
    except Exception:
        return {"status": "degraded", "redis": "down"}
    
    return {"status": "healthy"}
```

## 🔒 Security Checklist

- [ ] HTTPS enabled
- [ ] Strong JWT secret
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] CORS properly configured
- [ ] Security headers set
- [ ] Database access restricted
- [ ] Regular security updates
- [ ] Monitoring and alerting
- [ ] Backup strategy

## 🚀 Deployment Commands

```bash
# 1. Build and deploy with Docker Compose
docker-compose up -d

# 2. Check service status
docker-compose ps

# 3. View logs
docker-compose logs -f backend

# 4. Scale services
docker-compose up -d --scale backend=3

# 5. Update application
git pull
docker-compose build
docker-compose up -d
```

## 📈 Performance Optimization

### 1. Database Optimization
- Add indexes for frequently queried fields
- Use connection pooling
- Implement caching for static data

### 2. API Optimization
- Implement response caching
- Use async operations where possible
- Optimize database queries

### 3. Frontend Optimization
- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading

## 🔄 Backup Strategy

### 1. Database Backups
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL > backup_$DATE.sql
gzip backup_$DATE.sql
aws s3 cp backup_$DATE.sql.gz s3://your-backup-bucket/
```

### 2. Application Data
- Export user data regularly
- Backup configuration files
- Version control for code changes

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Verify network connectivity
   - Check database logs

2. **API Timeout Errors**
   - Increase timeout settings
   - Check external API limits
   - Monitor system resources

3. **Memory Issues**
   - Monitor memory usage
   - Implement connection pooling
   - Optimize queries

### Debug Commands

```bash
# Check service health
curl http://localhost:8000/health

# View application logs
docker-compose logs backend

# Check database connectivity
docker-compose exec db psql -U user -d investment_advisor

# Monitor system resources
docker stats
```

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test connectivity between services
4. Review security settings
5. Contact system administrator
