# Deployment Guide: Humanoid Robotics Learning Platform

## Overview

This guide covers deploying the personalization system (Phases 1-5) and frontend dashboard (Phase 6) to production.

## Environment Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Node.js 16+ (for frontend)
- Docker (optional, for containerization)
- Git

### Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/robotics_db

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=qdrant-key
QDRANT_COLLECTION_NAME=textbook_chunks

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false
ENVIRONMENT=production

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# Authentication
JWT_SECRET_KEY=your-super-secret-key-minimum-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
REACT_APP_ENVIRONMENT=production
```

**Security Note**: Never commit `.env` file to Git. Use environment variables in CI/CD.

## Database Setup

### Initialize PostgreSQL

```bash
# Create database
createdb robotics_db -U postgres

# Connect to database
psql -U postgres -d robotics_db

# Run migrations (Alembic)
alembic upgrade head
```

### Database Connection Pooling

In `backend/src/config.py`:

```python
from sqlalchemy.pool import NullPool, QueuePool

# For production: use QueuePool
SQLALCHEMY_ENGINE_OPTIONS = {
    "poolclass": QueuePool,
    "pool_size": 20,
    "max_overflow": 40,
    "pool_pre_ping": True,  # Test connections before using
}
```

### Database Indexes

Ensure indexes are created for performance:

```sql
-- User queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);

-- Progress queries
CREATE INDEX idx_progress_user_chapter ON progress(user_id, chapter_id);
CREATE INDEX idx_progress_user_completion ON progress(user_id, completion_status);

-- Conversation queries
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Message queries
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
```

## Backend Deployment

### Using Gunicorn + Uvicorn

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run with Gunicorn
gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  src.main:app
```

### Using Docker

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "src.main:app"]
```

Build and run:

```bash
docker build -t robotics-api .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e OPENAI_API_KEY="sk-..." \
  -e JWT_SECRET_KEY="your-secret-key" \
  robotics-api
```

### Using Systemd

Create `/etc/systemd/system/robotics-api.service`:

```ini
[Unit]
Description=Humanoid Robotics API
After=network.target postgresql.service

[Service]
Type=notify
User=robotics
WorkingDirectory=/opt/robotics-api
Environment="PATH=/opt/robotics-api/venv/bin"
ExecStart=/opt/robotics-api/venv/bin/gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000 \
  --timeout 120 \
  src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
systemctl enable robotics-api
systemctl start robotics-api
```

## Frontend Deployment

### Build

```bash
cd frontend
npm install
npm run build
```

### Using Nginx

Create `/etc/nginx/sites-available/robotics`:

```nginx
upstream robotics_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Frontend
    location / {
        root /var/www/robotics/frontend/build;
        try_files $uri /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://robotics_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        access_log off;
        proxy_pass http://robotics_api;
    }
}
```

Enable:

```bash
ln -s /etc/nginx/sites-available/robotics /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: robotics_db
      POSTGRES_USER: robotics
      POSTGRES_PASSWORD: secure-password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://robotics:secure-password@db:5432/robotics_db
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://api:8000/api/v1

volumes:
  postgres_data:
```

Deploy:

```bash
docker-compose up -d
```

## Monitoring & Logging

### Application Monitoring

Using Prometheus:

```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def add_metrics(request, call_next):
    request_count.inc()
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    request_duration.observe(duration)
    return response
```

### Logging Configuration

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "/var/log/robotics-api/app.log",
            "maxBytes": 104857600,  # 100MB
            "backupCount": 10,
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Error Tracking (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development")
)
```

## Security Checklist

- [ ] HTTPS enabled (SSL/TLS certificate)
- [ ] CORS properly configured (only allowed origins)
- [ ] JWT secret key is strong (>32 characters, random)
- [ ] Database password is secure
- [ ] API keys stored in environment variables (not in code)
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] Regular security updates applied
- [ ] Database backups configured
- [ ] Monitoring and alerting enabled
- [ ] Access logs reviewed regularly

## Backup & Recovery

### Database Backups

```bash
# Daily backup
0 2 * * * pg_dump robotics_db > /backups/db_$(date +\%Y\%m\%d).sql

# Restore from backup
psql robotics_db < /backups/db_20260101.sql
```

### Disaster Recovery Plan

1. **RTO** (Recovery Time Objective): < 1 hour
2. **RPO** (Recovery Point Objective): < 1 day
3. **Backup Strategy**: Daily automated backups to offsite storage
4. **Failover**: Load balancer automatically routes to backup instance

## Performance Optimization

### Query Optimization

```python
# Use selectinload for relationships
from sqlalchemy.orm import selectinload

query = select(User).options(
    selectinload(User.progress_records),
    selectinload(User.achievements)
)
```

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def get_learning_paths():
    # Cached for 1 hour
    return await fetch_learning_paths()
```

### Database Optimization

- Connection pooling
- Query result pagination
- Indexed frequently-used queries
- Denormalization for read-heavy tables

## Rollback Procedures

### Frontend Rollback

```bash
# If new version has issues
git checkout previous-version
npm run build
# Deploy previous build to web server
```

### Backend Rollback

```bash
# If API has issues
git checkout previous-version
docker-compose down
docker-compose up -d
```

### Database Rollback

```bash
# Alembic downgrade
alembic downgrade -1  # Revert last migration
```

## Health Checks

### Endpoint Status

```bash
# API health
curl https://yourdomain.com/health

# Database connectivity
curl https://yourdomain.com/ready

# Application status
curl https://yourdomain.com/
```

### Monitoring Alerts

Set up alerts for:
- API response time > 500ms
- Error rate > 1%
- Database connection pool exhausted
- Disk space < 10% remaining
- Memory usage > 80%

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificate installed
- [ ] CORS origins configured
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Logging configured
- [ ] Backups verified
- [ ] Load tests passed
- [ ] Security scan passed
- [ ] Documentation updated
- [ ] Team notified of deployment

## Support & Troubleshooting

### Common Issues

**Database connection timeout**
- Check PostgreSQL is running
- Verify connection string
- Check firewall rules
- Increase pool size

**API rate limiting**
- Check RATE_LIMIT_REQUESTS setting
- Review client behavior
- Adjust limits for trusted clients

**Authentication failures**
- Verify JWT_SECRET_KEY is consistent
- Check token expiration
- Review CORS settings

### Getting Help

- Check logs: `journalctl -u robotics-api -n 100`
- Monitor metrics: Prometheus dashboard
- Review error tracking: Sentry dashboard
- Contact: devops@roboticslearning.edu
