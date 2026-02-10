# System Architecture

Complete technical overview of the Hackathon1 Book Personalization System.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  React App   │  │  Dashboard   │  │   Pages      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│         └─────────────────┼─────────────────┘               │
│                           ↓                                  │
├──────────────────────────────────────────────────────────────┤
│                    REST API Layer (FastAPI)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Routes: /users, /progress, /dashboard, /api/v1/...  │  │
│  │ Auth: JWT Bearer Tokens                              │  │
│  │ Rate Limiting: 100 req/min per user                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↑↓                                │
├──────────────────────────────────────────────────────────────┤
│              Business Logic Layer (Services)                │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ UserService     │  │ Achievement  │  │ Statistics   │   │
│  │ - Register      │  │ Service      │  │ Service      │   │
│  │ - Login         │  │ - Detect     │  │ - Analyze    │   │
│  │ - Profile       │  │ - Award      │  │ - Recommend  │   │
│  └─────────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐   ┌───────────────┐  ┌──────────────┐    │
│  │ Progress     │   │ Practice      │  │ Recommendation   │
│  │ Service      │   │ Service       │  │ Engine           │
│  └──────────────┘   └───────────────┘  └──────────────┘    │
│                           ↑↓                                │
├──────────────────────────────────────────────────────────────┤
│           Data Access Layer (Repository Pattern)           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Database Queries, Caching, Connection Pooling      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           ↑↓                                │
├──────────────────────────────────────────────────────────────┤
│              Infrastructure Layer                           │
│  ┌──────────────────┐  ┌──────────────┐  ┌─────────────┐   │
│  │  PostgreSQL      │  │    Redis     │  │   Docker    │   │
│  │  - User data     │  │  - Caching   │  │ - Container │   │
│  │  - Achievements  │  │  - Sessions  │  │ - Compose   │   │
│  │  - Progress      │  │  - TTL       │  │             │   │
│  └──────────────────┘  └──────────────┘  └─────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Layer Breakdown

### 1. Frontend Layer

**Components:**
- React components for pages and features
- Protected routes with JWT verification
- Dashboard with progress visualization
- Achievement badge display

**Data Flow:**
- HTTP requests to FastAPI backend
- JWT token in Authorization header
- Handles token refresh on expiry
- Error handling and loading states

**Key Files:**
- `frontend/src/pages/` - Page components
- `frontend/src/components/` - Reusable components
- `frontend/src/hooks/` - Custom React hooks
- `frontend/src/utils/` - Utility functions

---

### 2. REST API Layer

**Framework:** FastAPI with 15+ endpoints

**Endpoints by Category:**

| Category | Count | Examples |
|----------|-------|----------|
| Authentication | 3 | register, login, refresh |
| User Profile | 2 | get profile, update profile |
| Progress | 4 | complete, practice, retry, metrics |
| Achievements | 1 | get achievements |
| Statistics | 1 | get statistics |
| Learning Paths | 2 | list paths, select path |
| Preferences | 2 | get/update preferences |
| Advanced | 1 | advanced challenges |
| Health | 3 | health, ready, cache status |

**Request/Response Format:**
```json
// Request
POST /api/v1/users/login
{
  "username": "john_doe",
  "password": "SecurePass123!"
}

// Response (200 OK)
{
  "status": "success",
  "data": {
    "access_token": "...",
    "token_type": "bearer"
  },
  "timestamp": "2026-02-07T10:30:00Z"
}
```

**Authentication:**
- JWT tokens with 30-minute access window
- Refresh tokens valid for 7 days
- Bearer token in Authorization header
- Automatic token validation on protected routes

---

### 3. Business Logic Layer

**Services** (pure Python classes):

#### UserService
- User registration and validation
- Password hashing with bcrypt
- Profile management
- Email uniqueness checking

#### ProgressService
- Chapter completion tracking
- Mastery score calculation
- Practice attempt recording
- Time tracking and statistics

#### AchievementService
- Automatic achievement detection
- XP calculation and tracking
- Streak detection (7-day, 30-day)
- 32 achievement types supported

#### StatisticsService
- Learning curve analysis
- Improvement rate calculation
- Plateau/regression detection
- Recommendation generation

#### RecommendationEngine
- Weak chapter identification
- Module prerequisite mapping
- Practice suggestion generation
- Priority ordering by efficiency

---

### 4. Data Access Layer

**Pattern:** Repository Pattern for database access

**Connection Management:**
- AsyncAdaptedQueuePool for async engines
- Pool size: 5 + 15 overflow connections
- Connection timeout: 30 seconds
- Pool recycling: 1 hour

**Caching Strategy:**
- Redis for frequently accessed data
- TTL: 1 hour for most data
- Pattern-based invalidation on updates
- Cache-aside pattern (read-through)

**Database Operations:**
- All async/await for non-blocking I/O
- SQLAlchemy ORM with typed models
- Transactional integrity for critical operations
- Migration management with Alembic

---

### 5. Infrastructure Layer

**PostgreSQL Database**
- Version: 15 (Alpine Linux)
- Tables: users, progress, achievements, preferences, etc.
- Indexes: 7 strategic indexes for performance
- 5-30x query improvement with indexes
- Connection pooling: 5-10x faster reuse

**Redis Cache**
- Version: 7 (Alpine Linux)
- AOF (Append-Only File) persistence
- In-memory caching with TTL
- 4-6x response improvement
- Pattern-based invalidation

**Docker Deployment**
- Docker Compose 3.9
- 3 services: PostgreSQL, Redis, FastAPI
- Health checks for all services
- Persistent named volumes
- Custom bridge network isolation
- &lt;20 second startup time

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React | 18.2 | UI framework |
| Frontend | TypeScript | 5.0 | Type safety |
| Backend | Python | 3.14 | Language |
| Backend | FastAPI | 0.100 | API framework |
| Backend | SQLAlchemy | 2.0 | ORM |
| Backend | Pydantic | 2.0 | Validation |
| Database | PostgreSQL | 15 | Primary DB |
| Cache | Redis | 7 | Cache layer |
| Deploy | Docker | 24.0 | Containerization |
| Deploy | Docker Compose | 2.0 | Orchestration |

---

## Data Model

### Core Tables

```
users
├── user_id (UUID, PK)
├── username (String, unique)
├── email (String, unique)
├── password_hash (String)
├── created_at (DateTime)
└── last_login (DateTime)

progress
├── progress_id (UUID, PK)
├── user_id (FK)
├── chapter_id (Integer)
├── mastery_score (Integer, 0-100)
├── time_spent_seconds (Integer)
├── completed_at (DateTime)
└── attempts (Integer)

achievements
├── achievement_id (UUID, PK)
├── user_id (FK)
├── achievement_type (String, unique per user)
├── title (String)
├── display_info_json (JSON)
├── earned_date (DateTime)
└── points (Integer)

preferences
├── preference_id (UUID, PK)
├── user_id (FK)
├── notification_email (Boolean)
├── dark_mode (Boolean)
└── updated_at (DateTime)
```

---

## Performance Characteristics

### Response Times

| Operation | Time | Optimization |
|-----------|------|--------------|
| Dashboard Load | &lt;50ms | Redis cache |
| DB Query | &lt;50ms | Strategic indexes |
| API Response | &lt;100ms | Combined |
| Cache Hit | &lt;10ms | Redis |
| Cache Miss | &lt;100ms | DB + cache write |

### Scalability

**Current Deployment:**
- Supports &lt;100 concurrent users
- ~600-700MB RAM total
- Single PostgreSQL instance
- Single Redis instance
- Single FastAPI instance

**Scaling to >100 Users:**
1. Add load balancer (nginx/HAProxy)
2. Multiple FastAPI instances
3. Shared PostgreSQL (managed service)
4. Shared Redis (managed service)
5. Kubernetes orchestration (optional)

---

## Security Architecture

### Authentication Flow
```
1. Register/Login → Create JWT tokens
2. Access Token → Valid for 30 minutes
3. Refresh Token → Valid for 7 days
4. Make Requests → Include access token
5. Token Expires → Use refresh token
6. Get New Token → Repeat
```

### Security Measures

| Measure | Implementation |
|---------|-----------------|
| Password | Bcrypt hashing with salt |
| Tokens | JWT with HS256 signature |
| CORS | Configured for allowed origins |
| Rate Limiting | 100 req/min per user |
| SQL Injection | Parameterized queries |
| XSS Protection | Input validation |
| HTTPS | Enforce in production |

---

## Development Workflow

### Local Setup
```bash
git clone <repo>
cd hackathon1-book
cp .env.docker .env
docker-compose up -d
pytest tests/  # Run tests
```

### Code Organization
```
backend/
├── src/
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── api/
│   │   ├── routes/       # API endpoints
│   │   └── dependencies/ # FastAPI dependencies
│   └── database/         # DB connection
├── tests/
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
└── alembic/              # Migrations
```

### Testing Strategy

**Test Types:**
- **Unit Tests**: Service methods in isolation
- **Integration Tests**: Database + service interactions
- **API Tests**: Full endpoint testing
- **Performance Tests**: Load and benchmark
- **Security Tests**: Auth, SQL injection, XSS

**Coverage Target:** 80%+

---

## Monitoring & Observability

### Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Readiness Check
curl http://localhost:8000/ready

# Cache Status
curl http://localhost:8000/health/cache
```

### Logging

```bash
# View all logs
docker-compose logs

# Follow API logs
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100
```

### Metrics

- Request count
- Response times (p95, p99)
- Database query times
- Cache hit/miss ratio
- Error rates by endpoint

---

## Next Steps

- **[Quick Start](/docs/deployment/quick-start)** - Set up locally
- **[API Reference](/docs/api)** - Explore endpoints
- **[Running Tests](/docs/development/running-tests)** - How to test

---

**Ready to explore the codebase?** Start with [Quick Start](/docs/deployment/quick-start).
