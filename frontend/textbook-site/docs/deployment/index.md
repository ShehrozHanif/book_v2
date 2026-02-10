# Deployment & Operations

Complete guide to deploying and operating the Hackathon1 Book Personalization System.

## Deployment Overview

The system is designed for production deployment using Docker Compose, supporting:

- **One-Command Deployment** - Single command to start all services
- **Automated Health Checks** - Services verify readiness
- **Data Persistence** - PostgreSQL and Redis data survives restarts
- **Zero-Downtime Updates** - Service restart policies for reliability
- **Production Security** - Environment variables for secrets
- **Performance Optimized** - Connection pooling, caching, indexes

## Quick Facts

| Property | Value |
|----------|-------|
| **Container Runtime** | Docker |
| **Orchestration** | Docker Compose 3.9 |
| **Services** | 3 (PostgreSQL, Redis, FastAPI) |
| **Startup Time** | 10-20 seconds |
| **Data Persistence** | Named volumes |
| **Network Isolation** | Custom bridge network |
| **Health Checks** | All services monitored |

## Architecture

```
                ┌──────────────────┐
                │   Load Balancer  │
                │   (nginx/HAProxy)│
                └────────┬─────────┘
                         │
         ┌───────────────┴───────────────┐
         ↓                               ↓
    ┌─────────┐                     ┌─────────┐
    │  FastAPI│ (Port 8000)         │  FastAPI│ (Port 8001)
    │  Server │                     │  Server │
    │    1    │                     │    2    │
    └────┬────┘                     └────┬────┘
         │                              │
         └──────────────┬───────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    ┌─────────┐   ┌─────────┐   ┌─────────┐
    │PostgreSQL   │  Redis  │   │ Shared  │
    │  (Primary)  │ (Cache) │   │ Storage │
    └─────────┘   └─────────┘   └─────────┘
```

**Single Server (Recommended for &lt;100 concurrent users):**
- 1 FastAPI instance
- 1 PostgreSQL instance
- 1 Redis instance
- ~600-700MB RAM total

**Multi-Server (For >100 concurrent users):**
- N FastAPI instances behind load balancer
- Shared PostgreSQL database
- Shared Redis cache
- Kubernetes orchestration

## Deployment Paths

1. **[Quick Start](/docs/deployment/quick-start)** - 5-minute local setup
2. **[Docker Deployment](/docs/deployment/docker-deployment)** - Production with Docker Compose
3. **[Environment Setup](/docs/deployment/environment)** - Configure secrets and settings
4. **[Health Monitoring](/docs/deployment/health-checks)** - Monitor service status
5. **[Troubleshooting](/docs/deployment/troubleshooting)** - Common issues and solutions

## What's Included

### Services

**PostgreSQL 15 (Database)**
- Persistent data storage
- Async driver support
- Health check: `pg_isready`
- Volume: `postgres_data`

**Redis 7 (Cache)**
- In-memory caching
- AOF persistence
- Health check: `redis-cli ping`
- Volume: `redis_data`

**FastAPI (API Server)**
- REST API with 15+ endpoints
- JWT authentication
- Health check: `GET /ready`
- Port: 8000 (configurable)

### Configuration Files

**docker-compose.yml** (124 lines)
- Service definitions with health checks
- Volume configuration
- Network setup
- Environment variables

**.env.docker** (28 lines)
- Database credentials
- API configuration
- Security settings
- Cache parameters

### Monitoring & Observability

- **Health Endpoints** - `/health`, `/ready` for monitoring
- **Logs** - Accessible via `docker-compose logs`
- **Metrics** - Database connection metrics, cache stats
- **Status** - `docker-compose ps` shows service health

## System Requirements

### Minimum (Development)
- **CPU**: 2 cores
- **RAM**: 1GB
- **Storage**: 10GB
- **OS**: Linux, macOS, Windows with Docker

### Recommended (Production)
- **CPU**: 4+ cores
- **RAM**: 4GB+
- **Storage**: 50GB+ (SSD)
- **OS**: Linux (CentOS, Ubuntu, Debian)
- **Database Backup**: Off-site backup for PostgreSQL

### Network Requirements
- **Ports**: 8000 (API), 5432 (PostgreSQL), 6379 (Redis)
- **Bandwidth**: 1Mbps minimum
- **Firewall**: Allow ingress to port 8000, restrict others

## Next Steps

1. **Quick Start** - Deploy locally in 5 minutes
2. **Environment Setup** - Configure production variables
3. **Docker Deployment** - Deploy to production
4. **Health Monitoring** - Set up monitoring
5. **Troubleshooting** - Debug any issues

## Support

- **Questions?** See relevant section below
- **Issues?** Check troubleshooting guide
- **Feedback?** Report on GitHub

---

**Ready to deploy?** Start with [Quick Start](/docs/deployment/quick-start).
