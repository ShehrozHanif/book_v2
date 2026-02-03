# RAG Chatbot - Production Deployment Guide

Complete guide for deploying the Humanoid Robotics Textbook RAG Chatbot to production.

## Table of Contents

1. [Quick Start (Local Development)](#quick-start-local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Database Setup](#database-setup)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start (Local Development)

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Git

### Start Full Stack

```bash
# Clone repository
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot

# Create .env file with your API keys
cp backend/.env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Verify all services are healthy
docker-compose ps
```

**Services:**

- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Qdrant: http://localhost:6333

### Stop Services

```bash
docker-compose down

# Remove volumes (careful - deletes data!)
docker-compose down -v
```

---

## Docker Deployment

### Build Images

```bash
# Build backend
cd backend
docker build -t rag-chatbot-backend:latest .

# Build frontend
cd ../frontend
docker build -t rag-chatbot-frontend:latest .
```

### Run with Docker Compose

```bash
# Production mode
docker-compose up -d

# With specific profile (e.g., production with nginx)
docker-compose --profile production up -d

# Scale backend (multiple workers)
docker-compose up -d --scale backend=3
```

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check all services
docker-compose ps
docker-compose logs backend
```

---

## Production Deployment

### Option 1: Cloud VPS (DigitalOcean, Linode, AWS EC2)

#### Server Requirements

- **CPU**: 2+ vCPUs
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB SSD
- **OS**: Ubuntu 22.04 LTS

#### Deployment Steps

1. **Provision Server**

```bash
# SSH into server
ssh user@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

2. **Clone and Configure**

```bash
# Clone repository
git clone https://github.com/yourusername/rag-chatbot.git
cd rag-chatbot

# Create production .env
nano .env
```

**Production .env:**

```env
# OpenAI
OPENAI_API_KEY=sk-prod-...

# Database
DATABASE_URL=postgresql+asyncpg://user:secure_password@postgres:5432/chatbot_db

# Qdrant
QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=secure_qdrant_key

# Logging
LOG_LEVEL=INFO
```

3. **Deploy with Docker Compose**

```bash
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

4. **Set Up Nginx Reverse Proxy**

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/rag-chatbot
```

**Nginx Configuration:**

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name roboticsbook.ai www.roboticsbook.ai;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name roboticsbook.ai www.roboticsbook.ai;

    # SSL certificates (use Certbot to generate)
    ssl_certificate /etc/letsencrypt/live/roboticsbook.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/roboticsbook.ai/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rag-chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

5. **SSL/TLS with Let's Encrypt**

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d roboticsbook.ai -d www.roboticsbook.ai

# Auto-renewal (test)
sudo certbot renew --dry-run
```

### Option 2: Vercel (Frontend) + Railway/Render (Backend)

#### Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel deploy --prod
```

**Vercel Configuration:**

Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://api.roboticsbook.ai"
  }
}
```

#### Deploy Backend to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway up
```

**Railway Configuration:**

- Set environment variables in Railway dashboard
- Connect PostgreSQL and Qdrant add-ons
- Configure custom domain

### Option 3: Kubernetes (Production Scale)

See `k8s/` directory for Kubernetes manifests (to be created if needed).

---

## Environment Configuration

### Required Environment Variables

#### Backend

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | Yes |
| `DATABASE_URL` | PostgreSQL connection | `postgresql+asyncpg://...` | Yes |
| `QDRANT_URL` | Qdrant endpoint | `http://qdrant:6333` | Yes |
| `QDRANT_API_KEY` | Qdrant API key | `secure-key` | No (local) |
| `LOG_LEVEL` | Logging level | `INFO` | No |

#### Frontend

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `REACT_APP_API_URL` | Backend API URL | `https://api.roboticsbook.ai` | Yes |

### Secrets Management

**Development**: Use `.env` files (never commit!)

**Production**: Use secrets management service

- **AWS**: AWS Secrets Manager
- **GCP**: Google Secret Manager
- **Azure**: Azure Key Vault
- **Railway/Render**: Built-in secrets
- **Docker**: Docker secrets

**Example with Docker Secrets:**

```bash
# Create secrets
echo "sk-prod-..." | docker secret create openai_api_key -
echo "postgresql://..." | docker secret create database_url -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - openai_api_key
      - database_url
```

---

## Database Setup

### PostgreSQL (Production)

#### Option 1: Managed Database (Recommended)

- **Neon**: Serverless PostgreSQL
- **Supabase**: PostgreSQL + additional features
- **AWS RDS**: Enterprise-grade
- **DigitalOcean Managed Databases**: Simple and reliable

#### Option 2: Self-Hosted

```bash
# Run PostgreSQL container
docker run -d \
  --name postgres \
  -e POSTGRES_USER=chatbot_user \
  -e POSTGRES_PASSWORD=secure_password \
  -e POSTGRES_DB=chatbot_db \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:15-alpine

# Initialize schema
docker exec -i postgres psql -U chatbot_user -d chatbot_db < backend/src/database/schema.sql
```

### Qdrant (Production)

#### Option 1: Qdrant Cloud (Recommended)

- Sign up at https://cloud.qdrant.io
- Create cluster
- Get API key and URL
- Update `QDRANT_URL` and `QDRANT_API_KEY`

#### Option 2: Self-Hosted

```bash
# Run Qdrant container
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest
```

### Backup Strategy

#### PostgreSQL Backups

```bash
# Manual backup
docker exec postgres pg_dump -U chatbot_user chatbot_db > backup_$(date +%Y%m%d).sql

# Automated daily backups (crontab)
0 2 * * * docker exec postgres pg_dump -U chatbot_user chatbot_db | gzip > /backups/chatbot_$(date +\%Y\%m\%d).sql.gz
```

#### Qdrant Backups

```bash
# Create snapshot
curl -X POST http://localhost:6333/collections/textbook_chunks/snapshots

# Download snapshot
curl -o qdrant_backup.snapshot http://localhost:6333/collections/textbook_chunks/snapshots/{snapshot_name}
```

---

## Monitoring and Logging

### Structured Logging

All logs are JSON-formatted for easy parsing.

**View logs:**

```bash
# Backend logs
docker-compose logs -f backend

# Tail specific service
docker logs -f rag-chatbot-backend --tail 100

# Search for errors
docker logs rag-chatbot-backend | grep ERROR
```

### Log Aggregation (Production)

#### Option 1: Elasticsearch + Kibana (ELK Stack)

```bash
# Add to docker-compose.yml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
    ports:
      - 9200:9200

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - 5601:5601
    depends_on:
      - elasticsearch
```

#### Option 2: Cloud Logging

- **Datadog**: Full observability platform
- **Logtail**: Simple log management
- **AWS CloudWatch**: AWS native
- **GCP Cloud Logging**: GCP native

### Metrics and Monitoring

**Key Metrics to Track:**

1. **Latency**: p50, p95, p99 response times
2. **Error Rate**: 5xx errors / total requests
3. **API Costs**: Daily OpenAI spending
4. **Database Performance**: Query execution time
5. **Retrieval Quality**: Average relevance scores

**Tools:**

- **Prometheus + Grafana**: Metrics and dashboards
- **Sentry**: Error tracking
- **UptimeRobot**: Uptime monitoring

---

## CI/CD Pipeline

### GitHub Actions

Pipeline is defined in `.github/workflows/ci.yml`.

**Workflow:**

1. **On Push/PR**: Run tests and linting
2. **On Merge to `develop`**: Deploy to staging
3. **On Merge to `main`**: Deploy to production

### Required GitHub Secrets

Configure in repository settings:

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for tests |
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub password |

### Manual Deployment

```bash
# Build and push images
docker build -t yourusername/rag-chatbot-backend:latest ./backend
docker push yourusername/rag-chatbot-backend:latest

docker build -t yourusername/rag-chatbot-frontend:latest ./frontend
docker push yourusername/rag-chatbot-frontend:latest

# Pull on server
ssh user@server
docker pull yourusername/rag-chatbot-backend:latest
docker-compose up -d
```

---

## Troubleshooting

### Backend not starting

**Check logs:**

```bash
docker-compose logs backend
```

**Common issues:**

1. Missing environment variables
2. Database connection failed
3. OpenAI API key invalid

### Frontend not loading

**Check logs:**

```bash
docker-compose logs frontend
```

**Common issues:**

1. `REACT_APP_API_URL` incorrect
2. CORS errors (check nginx config)
3. Build failed

### Database connection errors

```bash
# Test database connection
docker exec -it postgres psql -U chatbot_user -d chatbot_db

# Check DATABASE_URL format
# Correct: postgresql+asyncpg://user:pass@host:5432/db
```

### High API costs

```bash
# Monitor OpenAI usage
grep "cost=" logs/app.log | awk -F'cost=\\$' '{sum+=$2} END {print "Total: $" sum}'

# Reduce costs:
# 1. Cache frequent queries
# 2. Reduce max tokens in config
# 3. Use cheaper models (gpt-4o-mini)
```

---

## Performance Tuning

### Backend Optimization

**Uvicorn Workers:**

```bash
# In Dockerfile or docker-compose.yml
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Database Connection Pooling:**

```python
# In src/database/connection.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Frontend Optimization

**Code Splitting:**

```typescript
// Lazy load heavy components
const ChatBot = React.lazy(() => import('./components/ChatBot'));
```

**Caching:**

```nginx
# In nginx.conf
location /static/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Rollback Procedure

### Docker Rollback

```bash
# Tag current version before deploy
docker tag rag-chatbot-backend:latest rag-chatbot-backend:v1.2.3

# If deploy fails, rollback
docker-compose down
docker tag rag-chatbot-backend:v1.2.3 rag-chatbot-backend:latest
docker-compose up -d
```

### Database Rollback

```bash
# Restore from backup
docker exec -i postgres psql -U chatbot_user chatbot_db < backup_20240130.sql
```

---

## Security Checklist

- [ ] SSL/TLS enabled (HTTPS)
- [ ] API keys stored in secrets management
- [ ] Database passwords rotated quarterly
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Security headers set (CSP, HSTS, etc.)
- [ ] Regular dependency updates
- [ ] Vulnerability scanning enabled (Trivy)
- [ ] Logs sanitized (no PII)
- [ ] Backups encrypted

---

## Support

- **Documentation**: See `backend/DEPLOYMENT_README.md` and `frontend/DEPLOYMENT_README.md`
- **Issues**: GitHub Issues
- **Email**: support@roboticsbook.ai

---

**Last Updated**: 2024-01-30

**Version**: 1.0.0
