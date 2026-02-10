# Quick Start Guide

Get the Hackathon1 Book Personalization System running in 5 minutes.

## Prerequisites

Before starting, ensure you have:

- **Docker** (v20.10+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (v1.29+) - [Install Docker Compose](https://docs.docker.com/compose/install/)
- **Git** (v2.30+) - [Install Git](https://git-scm.com/downloads)
- **3 GB free disk space**
- **Ports 8000, 5432, 6379 available**

**Verify Installation:**
```bash
docker --version     # Should be 20.10.0+
docker-compose --version  # Should be 1.29.0+
git --version        # Should be 2.30.0+
```

## 5-Minute Setup

### Step 1: Clone Repository (1 min)
```bash
# Clone the project
git clone https://github.com/your-org/hackathon1-book.git
cd hackathon1-book

# Navigate to project root
pwd  # Should end in /hackathon1-book
```

### Step 2: Configure Environment (1 min)
```bash
# Copy configuration template
cp .env.docker .env

# For quick testing, default values are fine
# Edit for production (see Environment Setup guide)
nano .env  # or your favorite editor
```

**Minimal Configuration:**
```bash
# .env file
ENVIRONMENT=development
DEBUG=false
API_PORT=8000
SECRET_KEY=change-this-in-production
DB_PASSWORD=secure-password-here
```

### Step 3: Start Services (2 min)
```bash
# Start all services in background
docker-compose up -d

# Wait for services to become healthy (10-20 seconds)
sleep 15

# Check status
docker-compose ps
```

**Expected Output:**
```
NAME                   COMMAND                  STATUS
personalization-postgres    "docker-entrypoint..."   Up (healthy)
personalization-redis       "redis-server ..."       Up (healthy)
personalization-api         "uvicorn main:app..."    Up (healthy)
```

### Step 4: Verify API (1 min)
```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","timestamp":"2026-02-07T10:30:00Z"}

# Test API readiness
curl http://localhost:8000/ready

# Expected response:
# {"status":"ready","components":{"database":"ok","cache":"ok"}}
```

### Step 5: Access Application
```bash
# Open in browser
open http://localhost:8000/docs

# Or use curl to register
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!"
  }'
```

## Verify Installation

### Quick Tests

**Test Database Connection:**
```bash
docker-compose exec postgres psql -U personalization -c "SELECT 1;"
# Should return: 1
```

**Test Redis Connection:**
```bash
docker-compose exec redis redis-cli ping
# Should return: PONG
```

**Test API:**
```bash
# Check API version
curl http://localhost:8000/api/v1/health

# Should return JSON with version
```

**Check Service Logs:**
```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs api      # FastAPI logs
docker-compose logs postgres # Database logs
docker-compose logs redis    # Cache logs
```

## Common Commands

### Managing Services

**Start services:**
```bash
docker-compose up -d
```

**Stop services:**
```bash
docker-compose down
```

**Stop and remove data:**
```bash
docker-compose down -v
```

**Restart all services:**
```bash
docker-compose restart
```

**View status:**
```bash
docker-compose ps
```

### Viewing Logs

**All logs:**
```bash
docker-compose logs
```

**Follow logs (live):**
```bash
docker-compose logs -f api
```

**Last 100 lines:**
```bash
docker-compose logs --tail=100
```

### Running Commands

**Access PostgreSQL:**
```bash
docker-compose exec postgres psql -U personalization -d personalization_db
```

**Access Redis:**
```bash
docker-compose exec redis redis-cli
```

**Run tests:**
```bash
docker-compose exec api pytest tests/ -v
```

### Updating Configuration

**Edit environment variables:**
```bash
nano .env
docker-compose restart  # Restart for changes to take effect
```

**Update Docker images:**
```bash
docker-compose pull
docker-compose up -d
```

## Troubleshooting Quick Start

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
# Edit .env and change API_PORT, then restart
```

### Docker Not Responding
```bash
# Restart Docker daemon
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop      # macOS/Windows

# Or check Docker status
docker version
```

### Services Won't Start
```bash
# Check logs for errors
docker-compose logs api

# Verify ports are available
docker-compose ps

# Try rebuilding
docker-compose down
docker-compose up --build -d
```

### Health Checks Failing
```bash
# Give services more time to start
sleep 30
docker-compose ps

# Check individual service health
curl http://localhost:8000/ready
docker-compose exec redis redis-cli ping
```

## Next Steps

✅ **Congratulations!** System is running.

Now explore:

1. **API Documentation** - See `/docs/api`
2. **Personalization Features** - See `/docs/personalization`
3. **Environment Setup** - See `/docs/deployment/environment`
4. **Production Deployment** - See `/docs/deployment/docker-deployment`
5. **Monitoring** - See `/docs/deployment/health-checks`

## Common Tasks

### Register Test User
```bash
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

### Login and Get Token
```bash
curl -X POST http://localhost:8000/api/v1/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

### View API Documentation
```
Open browser to: http://localhost:8000/docs
```

### Check Database
```bash
docker-compose exec postgres psql -U personalization \
  -d personalization_db \
  -c "SELECT * FROM users LIMIT 1;"
```

## What's Running?

### FastAPI Server
- **URL**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Status**: http://localhost:8000/health

### PostgreSQL Database
- **Host**: localhost
- **Port**: 5432
- **User**: personalization
- **Database**: personalization_db
- **Connection**: `psql -U personalization -h localhost`

### Redis Cache
- **Host**: localhost
- **Port**: 6379
- **CLI**: `redis-cli -h localhost`

## Stopping Everything

When done, clean up:

```bash
# Stop all services
docker-compose down

# Stop and remove data (warning: data loss!)
docker-compose down -v

# Remove images too
docker-compose down -v --rmi all
```

## Getting Help

- **Issues?** See [Troubleshooting Guide](/docs/deployment/troubleshooting)
- **Questions?** Check [API Documentation](/docs/api)
- **Feature requests?** Submit on GitHub

---

**That's it!** You now have the personalization system running. 🎉

Next: [Environment Setup](/docs/deployment/environment) for production configuration.
