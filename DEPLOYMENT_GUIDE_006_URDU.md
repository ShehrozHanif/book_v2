# Deployment Guide: Urdu Translation Feature (T075)

**Feature**: 006-urdu-translation
**Version**: 1.0
**Last Updated**: February 10, 2026
**Owner**: Platform Team

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Database Setup](#database-setup)
3. [Backend Configuration](#backend-configuration)
4. [Frontend Configuration](#frontend-configuration)
5. [Data Seeding](#data-seeding)
6. [Monitoring & Observability](#monitoring--observability)
7. [Rollback Plan](#rollback-plan)
8. [Post-Deployment Verification](#post-deployment-verification)

---

## Pre-Deployment Checklist

Before deploying to production, verify:

### Code Review & Testing
- [ ] All tests passing: `pytest backend/src/personalization/tests/`
- [ ] Frontend tests passing: `npm test --coverage`
- [ ] Code review approved by 2+ engineers
- [ ] Security scan completed (SAST/DAST)
- [ ] Performance testing completed (response time <3s)

### Database Preparation
- [ ] Database backup created
- [ ] Backup stored in secure location
- [ ] Rollback plan documented and tested
- [ ] Migration scripts reviewed by DBA

### Infrastructure
- [ ] CDN configured for font files (Google Fonts)
- [ ] API rate limiting configured
- [ ] Monitoring alerts configured
- [ ] Logging collection enabled (ELK/Splunk)

### Documentation
- [ ] User documentation completed
- [ ] Admin documentation completed
- [ ] Runbooks created for common scenarios
- [ ] Communication plan to users prepared

### Stakeholder Sign-Off
- [ ] Product Manager approval
- [ ] Engineering Manager approval
- [ ] QA Lead sign-off
- [ ] DevOps Lead approval

---

## Database Setup

### 1. Run Migrations

```bash
# SSH into production server
ssh deploy@production-server

# Navigate to project
cd /var/app/hackathon1/book

# Create backup before migration
pg_dump -h <db-host> -U <db-user> -d <db-name> > /backups/pre-urdu-migration-$(date +%s).sql

# Run migration
alembic upgrade head

# Verify migration
alembic current
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgreSQLImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.migration] Running upgrade ... 00X_add_chatbot_translation.py
INFO  [alembic.migration] Running upgrade ... 00X_add_performance_indexes.py
```

### 2. Verify Tables Created

```sql
-- Connect to database
psql -h <db-host> -U <db-user> -d <db-name>

-- Check tables
\dt chatbot_response*
\dt glossary*
\dt user_language_preference

-- Check indexes
\di idx_*

-- Sample query
SELECT COUNT(*) FROM chatbot_response_template;
SELECT COUNT(*) FROM glossary_term;
```

**Expected Output**:
- 6 tables created
- 7 indexes created
- 0 rows initially (will be populated during seeding)

### 3. Configure Database Connection Pooling

**Edit `backend/.env.production`**:
```env
# Database Connection Pooling
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600
```

**Verify in application logs**:
```
INFO: Database pool initialized: size=10, max_overflow=20
```

---

## Backend Configuration

### 1. Environment Variables

Create `.env.production` with the following:

```env
# Core Settings
ENVIRONMENT=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@db-host:5432/dbname
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Authentication
JWT_ALGORITHM=HS256
JWT_EXPIRATION_SECONDS=86400

# API Configuration
API_RATE_LIMIT_GLOSSARY=100
API_RATE_LIMIT_ADMIN_TRANSLATIONS=50
API_RATE_LIMIT_ANALYTICS=200

# Cache Configuration
CACHE_ENABLED=True
CACHE_TTL_DASHBOARD=60
CACHE_TTL_TRANSLATIONS=300
CACHE_TTL_GLOSSARY=600

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_OUTPUT_PATH=/var/log/app/production.log

# Notifications (if enabled)
NOTIFICATION_EMAIL_ENABLED=True
NOTIFICATION_SMTP_SERVER=smtp.example.com
NOTIFICATION_SMTP_PORT=587
NOTIFICATION_WEBHOOK_ENABLED=True
NOTIFICATION_WEBHOOK_URL=https://webhook.example.com/translations
```

### 2. Update Application Configuration

**File**: `backend/src/config.py`

```python
from pydantic import BaseSettings

class ProductionSettings(BaseSettings):
    # Urdu Translation Feature
    URDU_FEATURE_ENABLED: bool = True
    URDU_FONT_CDN: str = "https://fonts.googleapis.com"

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_GLOSSARY: int = 100  # per minute
    RATE_LIMIT_ADMIN: int = 50      # per minute

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_RESPONSES: int = 300  # seconds

    class Config:
        env_file = ".env.production"
```

### 3. Enable Middleware

**File**: `backend/src/main.py`

```python
from fastapi import FastAPI
from backend.src.personalization.api.middleware.language import LanguageAuthMiddleware
from backend.src.personalization.api.rate_limiter import RateLimitMiddleware

app = FastAPI()

# Add rate limiting middleware
rate_limiter = RateLimiter()
app.add_middleware(RateLimitMiddleware, limiter=rate_limiter)

# Add language authentication middleware
app.add_middleware(LanguageAuthMiddleware)
```

### 4. Start Backend Service

```bash
# Using Gunicorn (recommended for production)
gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/app/access.log \
    --error-logfile /var/log/app/error.log \
    --log-level info \
    backend.src.main:app

# Or using systemd (recommended)
systemctl start hackathon1-backend
systemctl enable hackathon1-backend
```

---

## Frontend Configuration

### 1. Environment Variables

**File**: `.env.production`

```env
REACT_APP_API_BASE_URL=https://api.example.com/api/v1
REACT_APP_CHATBOT_ENABLED=true
REACT_APP_URDU_ENABLED=true
REACT_APP_FONT_CDN=https://fonts.googleapis.com
REACT_APP_LOG_LEVEL=info
```

### 2. Configure Font Loading

**File**: `frontend/public/index.html`

```html
<!-- Add to <head> -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
  /* Set font for Urdu content */
  [dir="rtl"],
  .urdu-text {
    font-family: 'Noto Naskh Arabic', 'Droid Arabic Naskh', serif;
    font-size: 16px;
    line-height: 1.6;
  }
</style>
```

### 3. Build Frontend

```bash
# Install dependencies
npm ci --production

# Build production bundle
npm run build

# Verify bundle size
ls -lh build/

# Expected: ~500KB for main bundle
```

### 4. Deploy Frontend

```bash
# Option 1: Deploy to CDN (S3 + CloudFront)
aws s3 sync build/ s3://example-bucket/static/app/ --delete
aws cloudfront create-invalidation --distribution-id E1234567 --paths "/*"

# Option 2: Deploy to web server
scp -r build/* deploy@production:/var/www/app/

# Verify deployment
curl https://app.example.com/ | grep "Chatbot"
```

---

## Data Seeding

### 1. Seed Glossary Terms

**Command**:
```bash
cd /var/app/hackathon1/book

# Seed from data file
python -m backend.scripts.load_glossary \
    --input backend/src/personalization/data/glossary_terms.json \
    --db-url postgresql://user:password@host:5432/db

# Options
--input: Path to JSON file with glossary terms
--batch-size: Number of terms to insert per transaction (default: 100)
--skip-duplicates: Skip terms that already exist (default: false)
--verify: Verify all terms loaded successfully (default: true)
```

**Verify Glossary**:
```sql
SELECT COUNT(*) as total_terms FROM glossary_term;
SELECT COUNT(*) as translated_terms FROM glossary_term WHERE urdu_translation IS NOT NULL;

-- Expected: 150+ terms with Urdu translations
```

### 2. Seed Response Templates

**Command**:
```bash
python -m backend.scripts.load_templates \
    --input backend/src/personalization/data/response_templates.json \
    --db-url postgresql://user:password@host:5432/db
```

**Verify Templates**:
```sql
SELECT COUNT(*) as total_templates FROM chatbot_response_template;
SELECT COUNT(*) as translated FROM chatbot_response_translation_status WHERE urdu_translation IS NOT NULL;

-- Expected: 50-100 core templates with Urdu translations
```

### 3. Create Sample Translations

```bash
python -m backend.scripts.seed_translations \
    --language urdu \
    --status published \
    --db-url postgresql://user:password@host:5432/db
```

**Verify Translations**:
```sql
SELECT status, COUNT(*) as count
FROM chatbot_response_translation_status
GROUP BY status;

-- Expected:
-- published | 50
-- reviewed  | 10
-- draft     | 5
```

---

## Monitoring & Observability

### 1. Configure Logging

**File**: `backend/src/personalization/api/logging_config.py`

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/app/translation.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "formatter": "json",
        }
    },
    "loggers": {
        "chatbot_translation": {
            "level": "INFO",
            "handlers": ["file"],
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### 2. Performance Metrics

Monitor these metrics via APM (New Relic, DataDog, etc.):

**API Response Times**:
```
/api/v1/chatbot/response/{template_key}: p95 < 500ms
/api/v1/glossary/search: p95 < 300ms
/api/v1/users/me/language-preference: p95 < 100ms
```

**Cache Performance**:
```
Translation cache hit rate: > 80%
Cache memory usage: < 50MB per instance
Cache invalidation latency: < 100ms
```

**Rate Limiting**:
```
Rate limit violations per hour: monitor for abuse
Glossary API: 100 req/min per user
Admin translations: 50 req/min per user
```

### 3. Alerts

Configure alerts in your monitoring system:

```
AlertName: HighTranslationResponseTime
Condition: p95(api.chatbot.response_time) > 1000ms
Action: Page on-call engineer
Severity: Warning

AlertName: RateLimitAbuse
Condition: rate_limit_violations > 100 per hour
Action: Alert security team
Severity: Critical

AlertName: CacheMemoryLeak
Condition: cache_memory_usage > 100MB
Action: Alert platform team
Severity: Warning
```

---

## Rollback Plan

### Quick Rollback (Emergency)

If critical issues are discovered immediately after deployment:

```bash
# 1. Disable feature flag (if implemented)
curl -X POST https://api.example.com/admin/feature-flags \
  -H "Authorization: Bearer <token>" \
  -d '{"feature": "urdu_translation", "enabled": false}'

# 2. Revert to previous backend version
systemctl stop hackathon1-backend
git checkout <previous-tag>
npm run build && npm run start
systemctl start hackathon1-backend

# 3. Revert frontend
aws cloudfront create-invalidation --distribution-id E1234567 --paths "/*"
aws s3 cp s3://example-bucket/backups/frontend-v1.0/ s3://example-bucket/static/app/ --recursive

# 4. Verify rollback
curl https://api.example.com/health
```

### Database Rollback

If database issues occur:

```bash
# 1. Restore from backup
pg_restore -h <db-host> -U <db-user> -d <db-name> /backups/pre-urdu-migration.sql

# 2. Run downgrade migration
alembic downgrade -1

# 3. Verify
psql -h <db-host> -U <db-user> -d <db-name> -c "SELECT * FROM alembic_version;"
```

For detailed rollback instructions, see: `backend/alembic/versions/00Y_rollback_chatbot_translation.py`

---

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://api.example.com/health
# Expected: {"status": "healthy", "version": "1.0"}

curl https://api.example.com/api/v1/chatbot/languages
# Expected: {"supported_languages": ["english", "urdu"], "default": "english"}
```

### 2. Smoke Tests

```bash
# Test authentication gate
curl -X GET https://api.example.com/api/v1/chatbot/response/greeting
# Expected: 401 Unauthorized (Urdu requires auth)

# Test authenticated access
curl -X GET https://api.example.com/api/v1/chatbot/response/greeting \
  -H "Authorization: Bearer <valid-token>" \
  -H "Accept: application/json"
# Expected: 200 OK with response

# Test language preference
curl -X PUT https://api.example.com/api/v1/users/me/language-preference \
  -H "Authorization: Bearer <valid-token>" \
  -H "Content-Type: application/json" \
  -d '{"language": "urdu"}'
# Expected: 200 OK

# Test glossary
curl -X GET 'https://api.example.com/api/v1/glossary/search?q=ROS&language=urdu' \
  -H "Authorization: Bearer <valid-token>"
# Expected: 200 OK with results
```

### 3. Performance Verification

```bash
# Using Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer <token>" \
  https://api.example.com/api/v1/chatbot/response/greeting
# Expected: p95 < 500ms

# Using wrk
wrk -t4 -c100 -d30s \
  -H "Authorization: Bearer <token>" \
  https://api.example.com/api/v1/glossary/search?q=ROS
# Expected: p95 < 300ms
```

### 4. Frontend Verification

```bash
# Check fonts are loading
curl -I https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic
# Expected: 200 OK

# Check RTL styling
curl https://app.example.com | grep "dir=\"rtl\""
# Expected: HTML contains RTL directive

# Test language toggle
# Manual: Login → Click Urdu button → Verify RTL direction applied
```

### 5. User Communication

- [ ] Send announcement to users: "Urdu language support now available!"
- [ ] Update documentation
- [ ] Monitor support tickets for issues
- [ ] Celebrate! 🎉

---

## Troubleshooting

### Issue: Urdu content not displaying

**Symptoms**: Users see boxes (□) or question marks instead of Urdu text

**Solution**:
1. Verify font is loading: Check DevTools → Network → Fonts
2. Clear browser cache: `Ctrl+Shift+Delete`
3. Verify database has translations: `SELECT COUNT(*) FROM glossary_term WHERE urdu_translation IS NOT NULL;`
4. Check font-family in CSS: Should be 'Noto Naskh Arabic'

### Issue: Rate limiting too strict

**Symptoms**: Legitimate users getting 429 Too Many Requests

**Solution**:
1. Check current limits: `cat backend/src/personalization/api/rate_limiter.py`
2. Increase if needed: Update `ENDPOINT_LIMITS` dictionary
3. Redeploy: `systemctl restart hackathon1-backend`

### Issue: Performance degradation

**Symptoms**: Response time > 3 seconds

**Solution**:
1. Check cache hit rate: Monitor `cache_hits / total_requests`
2. Verify indexes: `EXPLAIN ANALYZE SELECT ...`
3. Check database connection pool: Monitor pool_size vs waiting connections
4. Scale horizontally: Add more backend instances

---

## Rollback Sign-Off

If rollback is needed, follow this sign-off:

- [ ] Engineering Lead: _________________ Date: _______
- [ ] DevOps Lead: _________________ Date: _______
- [ ] Product Manager: _________________ Date: _______
- [ ] Customer Success: _________________ Date: _______

---

## Success Criteria

Deployment is successful when:

✅ All health checks pass
✅ Performance metrics within targets
✅ No critical errors in logs
✅ Users can switch to Urdu
✅ Glossary works with Urdu search
✅ RTL rendering correct
✅ Rate limiting functional
✅ Monitoring alerts active

---

**Deployment Completed**: ___/___/_____ by _________________
