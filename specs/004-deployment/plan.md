# Implementation Plan: Production Deployment System

**Branch**: `004-deployment` | **Date**: 2026-02-04 | **Spec**: [004-deployment/spec.md](./spec.md)

**Status**: Draft - Planning Complete
**Input**: Feature specification from `specs/004-deployment/spec.md`

---

## Summary

Deploy fully-functional RAG chatbot with personalization system to production across three serverless platforms (GitHub Pages frontend, Render backend, Neon PostgreSQL database) with automated CI/CD, health monitoring, and rollback capabilities. System must achieve 99.9% uptime, <3 second chat response time, and <$30/month cost while maintaining zero data loss and GDPR compliance.

---

## Technical Context

**Language/Version**: Python 3.9+ (backend), React 18+ (frontend), PostgreSQL 14+

**Primary Dependencies**:
- Backend: FastAPI, SQLAlchemy, asyncpg, uvicorn, python-jose (JWT), passlib (password hashing)
- Frontend: React, react-scripts, gh-pages (deployment)
- Database: Neon PostgreSQL (serverless), Qdrant Cloud (vector DB), OpenAI API (LLM)
- DevOps: GitHub Actions (CI/CD), Render (PaaS), GitHub Pages (static hosting)

**Storage**: PostgreSQL (Neon serverless) for relational data; Qdrant Cloud for vector embeddings

**Testing**: pytest (backend unit/integration), React Testing Library (frontend), end-to-end via deployment validation

**Target Platform**: Web (serverless cloud - GitHub Pages + Render + Neon)

**Project Type**: Web application (frontend SPA + backend API + serverless database)

**Performance Goals**:
- Chat response time: P95 <3 seconds
- Frontend page load: <2 seconds
- Uptime: 99.9% (43 minutes max downtime/month)
- Concurrent users: ~10 (Neon free tier), scaling to 100+ with paid tier

**Constraints**:
- Free tier deployment (0.5GB Neon storage, 512MB Render RAM, 15-min spin-down)
- Cold start penalty on Render (30-60 seconds after wake)
- Neon free tier connection limit (5 concurrent connections)
- Monthly cost must stay <$30 (excluding OpenAI API)

**Scale/Scope**:
- Users: 100-1000 (free tier), grows to 10k+ (requires upgrade)
- Data: 20 indexed chapters (~10MB vector embeddings), user data <1GB
- Code: ~8500 lines existing code (phases 1-3)

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| **Specification-Driven** | All work justified by spec | ✅ PASS - Spec complete with 7 stories, 25 requirements |
| **Production Readiness** | Error handling, testing, monitoring | ✅ PASS - Health checks, alerting, CORS, rate limiting specified |
| **Code Quality** | Tested, documented, composable | ✅ PASS - Existing code from phases 1-3 tested; new code follows patterns |
| **Educational Excellence** | N/A for deployment phase | ✅ PASS - Content already validated in phases 2-3 |
| **User-Centric Design** | Authentication, personalization | ✅ PASS - Auth preserved, personalization carried forward to production |

**No violations identified.** Proceeding to Phase 0.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-deployment/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (deployment decisions & best practices)
├── data-model.md        # Phase 1 output (database schema, entities, contracts)
├── quickstart.md        # Phase 1 output (deployment walkthrough)
├── contracts/           # Phase 1 output (API specs, config templates)
│   ├── neon-schema.sql  # Database initialization script
│   ├── render-config.yml # Backend deployment configuration
│   ├── github-pages.yml # Frontend deployment configuration
│   └── env-template.txt # Environment variables template
└── checklists/
    ├── requirements.md   # Quality validation (complete)
    └── deployment.md     # Go-live checklist (Phase 1 output)
```

### Source Code (repository root)

```text
# Existing code from phases 1-3 (production-ready, no changes for Phase 4)
backend/
├── src/
│   ├── main.py              # FastAPI entry point (ready)
│   ├── config.py            # Configuration loader (ready)
│   ├── database/
│   │   ├── connection.py    # Async connection pooling (NullPool - ready for serverless)
│   │   └── schema.sql       # Database schema (ready)
│   ├── api/
│   │   ├── routes/          # API endpoints
│   │   └── error_handler.py # Error handling (ready)
│   └── models/              # Data models
├── .env.example             # Updated with production examples
├── requirements.txt         # All dependencies listed
└── Dockerfile               # For deployment reference

frontend/
├── src/
│   ├── App.tsx              # React entry point (ready)
│   ├── services/
│   │   ├── chatApi.ts       # API client (uses env vars)
│   │   └── personalizationApi.ts
│   └── components/
├── package.json             # Updated with gh-pages scripts & homepage
├── .env.production           # Created - Render backend URL
└── Dockerfile               # For deployment reference

# New files for Phase 4 (created by planning/implementation)
.github/
├── workflows/
│   ├── deploy-backend.yml   # Render auto-deploy trigger
│   └── deploy-frontend.yml  # GitHub Pages deploy trigger

# Configuration files (environment-specific, not committed)
.env.production              # Production secrets (local reference, not in git)
.env.staging                 # Staging environment (if used)

# Deployment documentation
DEPLOYMENT_GUIDE.md          # Step-by-step deployment instructions
DEPLOYMENT_STATUS.md         # Current deployment status & monitoring
QUICK_START.md               # 3-step deployment guide
```

**Structure Decision**: Web application with separated frontend (React SPA) and backend (FastAPI). Frontend deployed to GitHub Pages (static), backend to Render (managed PaaS), database on Neon (serverless PostgreSQL). This matches existing code organization from phases 1-3. GitHub Actions provides CI/CD automation for both frontend and backend deployments.

---

## Implementation Phases

### Phase 0: Research & Design Decisions (1-2 hours)

**Objectives**: Resolve architectural decisions, establish best practices, document trade-offs

**Deliverables**:
1. `research.md` - Document answers to:
   - Monitoring stack choice (Render native vs DataDog vs alternatives)
   - Alert delivery method (email vs Slack vs PagerDuty)
   - Backup retention policy for Neon free tier
   - Upgrade path documentation from free to paid tiers
   - Cold start mitigation strategies
   - Secret rotation procedures

2. Decision tables comparing options for:
   - Deployment automation approaches
   - Health check implementation
   - Error tracking & logging
   - Database migration strategy

**Tasks** (to be detailed in research.md):
- Research Render deployment best practices for Python/FastAPI
- Research GitHub Pages deployment for React SPA
- Research Neon serverless PostgreSQL setup & connection pooling
- Research CI/CD patterns for multi-platform deployment
- Research monitoring & alerting for free-tier services
- Research disaster recovery for serverless architectures

---

### Phase 1: Architecture & Design (2-3 hours)

**Prerequisites**: Phase 0 research.md complete

**Deliverables**:

1. **data-model.md** - Document entities & schema:
   - User (id, email, password_hash, created_at, updated_at)
   - Conversation (id, user_id FK, created_at, expires_at)
   - Message (id, conversation_id FK, role, content, timestamp)
   - TextbookChunk (id, content, module, chapter, section)
   - AuditLog (id, query, response, relevance_scores, timestamp)
   - Personalization tables (user_profiles, achievements, progress, etc.)
   - Index strategy for performance
   - Validation rules from requirements

2. **contracts/** - Deployment configurations:
   - `neon-schema.sql` - Complete database initialization (9 tables with indexes)
   - `render-config.yml` - Render Web Service configuration
   - `github-pages.yml` - GitHub Pages deployment settings
   - `env-template.txt` - Environment variables with descriptions
   - `github-actions-deploy.yml` - CI/CD workflow examples

3. **quickstart.md** - Deployment walkthrough:
   - Step-by-step account setup (Neon, Render, GitHub Pages)
   - Configuration checklist
   - Deployment commands
   - Verification steps
   - Troubleshooting guide

4. **checklists/deployment.md** - Go-live checklist:
   - Pre-flight checks (all systems ready?)
   - Deployment steps (create accounts, configure, deploy)
   - Verification checks (frontend loads, backend responds, database connects, chat works)
   - Post-deployment validation (monitoring, performance, cost)
   - Rollback procedures (if issues detected)

5. **API Contracts** (from functional requirements):
   - Frontend to Backend: Chat API (`/api/v1/chat`), auth endpoints, personalization endpoints
   - Backend to Qdrant: Vector search queries
   - Backend to OpenAI: LLM completion requests
   - Environment variable contracts (15 backend, 1 frontend)

---

### Phase 2: Task Breakdown (1 hour)

**Prerequisites**: Phase 1 architecture complete

**Output**: `tasks.md` with ~30-50 detailed tasks organized by:

1. **Setup & Configuration (6-8 tasks)**
   - Create Neon account & database
   - Create Render account & service
   - Configure GitHub Pages
   - Initialize environment variables

2. **Backend Deployment (8-10 tasks)**
   - Set up Render Web Service
   - Configure build command & start command
   - Set environment variables
   - Test health endpoints
   - Verify database connection
   - Test API endpoints

3. **Frontend Deployment (6-8 tasks)**
   - Update package.json (gh-pages, homepage)
   - Create .env.production
   - Build production bundle
   - Deploy to GitHub Pages
   - Verify site loads

4. **CI/CD Automation (4-6 tasks)**
   - Create GitHub Actions workflows
   - Set up auto-deploy on git push
   - Configure rollback procedures
   - Test deployment pipeline

5. **Monitoring & Alerting (4-6 tasks)**
   - Set up health check monitoring
   - Configure basic alerts
   - Create monitoring dashboard
   - Document alert response procedures

6. **Documentation & Validation (4-6 tasks)**
   - Create deployment guide
   - Create runbooks (operations procedures)
   - Perform end-to-end testing
   - Verify success criteria met

**Task Dependencies**:
- Neon setup → Backend config → Backend deploy → Frontend deploy
- GitHub Pages setup → Frontend deploy
- All deploys → Monitoring setup → Testing

---

## Critical Path & Sequencing

```
Phase 0: Research (1-2 hours)
  ↓
Phase 1: Design (2-3 hours)
  ├─ data-model.md
  ├─ contracts/ (configs)
  ├─ quickstart.md
  └─ checklists/deployment.md
  ↓
Phase 2: Tasks (1 hour)
  └─ tasks.md (30-50 tasks, sequenced by dependencies)
```

**Estimated Total Planning**: 4-6 hours
**Estimated Implementation** (Phase 2 tasks): 40-60 minutes (following checklists, most automated)

---

## Key Decisions & Rationale

| Decision | Rationale | Alternatives Rejected |
|----------|-----------|----------------------|
| **GitHub Pages + Render + Neon** | Serverless, no ops burden, free tier, integrates with GitHub | AWS/GCP (more complex), traditional VMs (requires maintenance) |
| **Free tier deployment** | Lower cost for launch, suitable for initial traffic | Paid tiers (unnecessary upfront cost) |
| **NullPool connection pooling** | Works with serverless, no persistent connections | Traditional pooling (incompatible with Render spin-down) |
| **GitHub Actions for CI/CD** | Native GitHub integration, free for public repos | Jenkins/GitLab CI (additional setup), manual deployment (error-prone) |
| **Environment variables for secrets** | No secrets in git, easy rotation | .env files (security risk), hardcoded values (maintenance nightmare) |
| **Render auto-deploy on git push** | Eliminates manual deployment risk, enables rapid iteration | Manual deployment (error-prone), scheduled deploys (slower feedback) |

---

## Constraints & Trade-offs

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| **Free tier spin-down** (15 min inactivity) | Cold start 30-60 sec | Document in user guide; offer paid tier upgrade |
| **Neon connection limit** (5 free tier) | Database exhaustion risk | NullPool prevents this; scale if needed |
| **Neon storage limit** (0.5GB free tier) | Space concerns | Monitor usage; upgrade plan if needed |
| **Render RAM limit** (512MB free tier) | Memory pressure | Monitor; upgrade plan if needed |
| **OpenAI API costs** | Variable expense | Rate limiting (10 req/min); monitor usage |
| **GitHub Pages cold regions** | Slower for some users | Not addressed in Phase 4 (Phase 5 custom domain) |

---

## Success Criteria Mapping to Implementation

| Success Criteria | Implementation Task | Verification Method |
|-----------------|--------------------|--------------------|
| SC-001: Frontend loads <2 sec | Build optimize, GitHub Pages setup | Lighthouse audit |
| SC-002: Chat response <3 sec | Backend config, Render setup | Manual testing |
| SC-003: Database connect works | Neon setup, schema init | Connection test |
| SC-004: 20 chapters indexed | Qdrant pre-indexed (no action) | Vector search test |
| SC-005: 99.9% uptime | Health check monitoring | 7-day uptime report |
| SC-006: Health check 200 OK | Backend /health endpoint (exists) | curl test |
| SC-007: CORS configured | Backend env var setting | Browser test |
| SC-008: Env vars set (15) | Render environment section | Configuration audit |
| SC-009: Schema created (9 tables) | Neon schema.sql execution | SQL query test |
| SC-010: Auto-deploy on push | GitHub Actions workflow | Git push test |
| SC-011: Rollback <5 min | Render rollback procedure | Deployment test |
| SC-012: Monitoring dashboard | Basic dashboard creation | Visual check |
| SC-013: Alerts trigger | Alert threshold testing | Manual trigger test |
| SC-014: Zero data loss | Backup verification | Data integrity test |
| SC-015: End-to-end auth | Auth flow testing | User signup/login test |
| SC-016: Cost <$30/month | Cost tracking, free tiers used | Invoice review |

---

## Known Unknowns (Phase 0 Research)

The following will be clarified in Phase 0 research.md:

1. **Monitoring & Alerting**:
   - Which monitoring tool? (Render native dashboard vs DataDog vs Prometheus/Grafana)
   - Alert delivery method? (email vs Slack vs PagerDuty vs SMS)
   - Alert thresholds? (error rate >1%, latency >5sec, uptime <99.9%)

2. **Backup & Disaster Recovery**:
   - Backup retention policy? (Neon auto-backups, manual snapshots)
   - Recovery time objective (RTO)? (<1 hour)
   - Recovery point objective (RPO)? (<1 hour)

3. **Upgrade & Scaling Path**:
   - When to upgrade from free to paid tiers?
   - Cost of paid tiers (Render $7/month, Neon usage-based)
   - Scaling procedures documented?

4. **Cold Start Mitigation**:
   - Keep-alive pings for Render? (GitHub Actions scheduled task)
   - Documentation for users about cold start?
   - Consider paid tier if cold start unacceptable?

5. **Secret Rotation**:
   - How often to rotate API keys?
   - Procedure for secret rotation without downtime?
   - Automated secret expiration?

---

## Next Steps

1. **Phase 0** (1-2 hours): Run research tasks to resolve unknowns
   - Document findings in `research.md`
   - Create decision tables
   - Establish best practices

2. **Phase 1** (2-3 hours): Create architecture & contracts
   - Generate `data-model.md`
   - Create `contracts/` directory with configs
   - Write `quickstart.md` deployment guide
   - Create `checklists/deployment.md` go-live checklist

3. **Phase 2** (1 hour): Generate detailed tasks
   - Run `/sp.tasks 004-deployment` to create `tasks.md`
   - Detailed step-by-step tasks with sequencing
   - Assign resources and estimate effort

4. **Implementation** (40-60 min): Follow checklists and complete tasks
   - Execute deployment in phases
   - Verify success criteria
   - Document lessons learned

---

## Related Documentation

- **Constitution**: `.specify/memory/constitution.md` (project principles)
- **Specification**: `specs/004-deployment/spec.md` (7 stories, 25 requirements, 16 criteria)
- **Quality Checklist**: `specs/004-deployment/checklists/requirements.md` (validation: 40/40 pass)
- **Deployment Docs**: `DEPLOYMENT_GUIDE.md`, `QUICK_START.md` (created in preparation)

---

**Plan Status**: ✅ Draft Complete - Ready for Phase 0 Research

**Next Command**: Generate detailed research (Phase 0) → Complete Phase 1 architecture → Generate tasks (Phase 2)
