# Local Development Setup Guide

## Quick Start (5 minutes)

### 1. Backend Setup

```bash
# Clone repository
git clone https://github.com/your-org/robotics-learning.git
cd robotics-learning/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy template)
cp .env.example .env

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000

### 2. Frontend Setup

```bash
# In separate terminal
cd robotics-learning/frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start development server
npm start
```

Application available at: http://localhost:3000

## Detailed Setup

### Prerequisites

- Python 3.9+ (check: `python --version`)
- Node.js 16+ (check: `node --version`)
- PostgreSQL 13+ (check: `psql --version`)
- Git (check: `git --version`)

### Backend Configuration

#### Step 1: Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Database Setup

```bash
# Create PostgreSQL database and user
psql -U postgres -c "CREATE DATABASE robotics_db;"
psql -U postgres -c "CREATE USER robotics WITH PASSWORD 'dev-password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE robotics_db TO robotics;"

# Or use Docker for PostgreSQL
docker run --name robotics-db \
  -e POSTGRES_DB=robotics_db \
  -e POSTGRES_USER=robotics \
  -e POSTGRES_PASSWORD=dev-password \
  -p 5432:5432 \
  -d postgres:13
```

#### Step 3: Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://robotics:dev-password@localhost:5432/robotics_db

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-...

# Qdrant (if running locally)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=qdrant-key
QDRANT_COLLECTION_NAME=textbook_chunks

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
ENVIRONMENT=development

# Authentication
JWT_SECRET_KEY=dev-secret-key-at-least-32-characters-long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

#### Step 4: Initialize Database

```bash
# Run migrations
alembic upgrade head

# Seed test data (optional)
python -m scripts.seed_data
```

#### Step 5: Run Backend

```bash
# Development mode (with auto-reload)
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or with Gunicorn
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker src.main:app
```

### Frontend Configuration

#### Step 1: Node Environment

```bash
cd frontend

# Install dependencies
npm install

# Optional: Use node version manager
nvm use  # Uses version from .nvmrc
```

#### Step 2: Environment Variables

Create `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_ENVIRONMENT=development
```

#### Step 3: Run Frontend

```bash
# Development mode
npm start

# Runs on http://localhost:3000
```

#### Step 4: Build for Production

```bash
npm run build

# Output in frontend/build/
```

### Vector Database Setup (Qdrant)

```bash
# Using Docker
docker run -p 6333:6333 \
  -e QDRANT_API_KEY=qdrant-key \
  qdrant/qdrant:latest

# API available at http://localhost:6333
```

### Testing Setup

#### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/personalization/test_auth.py

# Run tests matching pattern
pytest -k "test_login"

# Run with verbose output
pytest -v
```

#### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- test/services/personalizationApi.test.ts
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new_field to users table"

# View migration files
ls alembic/versions/

# Apply all migrations
alembic upgrade head

# Upgrade to specific revision
alembic upgrade a1b2c3d4e5f6

# Downgrade one revision
alembic downgrade -1

# Show migration history
alembic history
```

### Code Quality Tools

#### Linting

```bash
# Backend (Python)
cd backend
pip install flake8 black isort
flake8 src/
black src/
isort src/

# Frontend (JavaScript/TypeScript)
cd frontend
npm run lint
npm run lint:fix
```

#### Type Checking

```bash
# Backend
mypy src/

# Frontend
tsc --noEmit
```

### Common Issues & Solutions

**Issue: Database connection refused**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# If not running:
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Linux
```

**Issue: OpenAI API key errors**
- Verify key is correct: `echo $OPENAI_API_KEY`
- Check key has API access enabled
- Regenerate key if needed

**Issue: Frontend won't connect to API**
- Check backend is running: `curl http://localhost:8000/health`
- Verify CORS settings in backend
- Check REACT_APP_API_URL in frontend .env

**Issue: Port already in use**
```bash
# Kill process on port
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
# Or use different port
uvicorn src.main:app --port 8001
```

### IDE Setup

#### VS Code (Recommended)

Install extensions:
- Python
- Pylance
- Flask
- REST Client (for API testing)
- Thunder Client (for API testing)
- ES7+ React/Redux/React-Native snippets
- TypeScript Vue Plugin

#### PyCharm

- File → Settings → Project → Python Interpreter
- Select virtual environment
- Enable poetry support if using poetry

### Git Workflow

```bash
# Clone repository
git clone <repo-url>
cd book

# Create feature branch
git checkout -b feature/personalization-dashboard

# Make changes
git add .
git commit -m "feat: add user dashboard component"

# Push to remote
git push origin feature/personalization-dashboard

# Create pull request on GitHub
```

### Documentation

- API docs: http://localhost:8000/docs (Swagger UI)
- API schema: http://localhost:8000/openapi.json (ReDoc)
- Component storybook: `npm run storybook` (frontend)

### Performance Testing

```bash
# Backend load testing with Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Frontend performance audit
npm run build:analyze
```

### Debugging

#### Backend Debugging

```python
# Add breakpoint in code
breakpoint()  # Python 3.7+

# Run with debugger
python -m pdb -m pytest tests/test_auth.py
```

#### Frontend Debugging

```javascript
// Add debugger statement
debugger;

// Or use Chrome DevTools
// F12 → Sources tab → Set breakpoints
```

### Environment Checklists

**First Time Setup:**
- [ ] Clone repository
- [ ] Create Python virtual environment
- [ ] Install Python dependencies
- [ ] Create PostgreSQL database
- [ ] Create backend .env file
- [ ] Run database migrations
- [ ] Start backend server
- [ ] Install Node dependencies
- [ ] Create frontend .env file
- [ ] Start frontend dev server
- [ ] Test login flow

**Daily Development:**
- [ ] Activate virtual environment
- [ ] Pull latest changes
- [ ] Start PostgreSQL
- [ ] Start backend server
- [ ] Start frontend server
- [ ] Run tests before committing

### Useful Commands

```bash
# Backend
source venv/bin/activate          # Activate venv
deactivate                        # Deactivate venv
pip list                          # List installed packages
pip freeze > requirements.txt     # Update requirements
alembic history                   # View migrations
pytest -v                         # Run tests verbosely

# Frontend
npm list                          # List packages
npm update                        # Update packages
npm run type-check               # Check TypeScript
npm run test -- --watch         # Watch tests
npm run build                    # Production build
```

### Getting Help

- Check logs: `tail -f /tmp/app.log`
- Read documentation: `/docs` folder
- Ask team: #dev-help Slack channel
- Search issues: GitHub Issues
- Contact: dev-support@roboticslearning.edu

### Next Steps

After setup:
1. Read `ARCHITECTURE.md` for system overview
2. Review `backend/README_PHASE6.md` for dashboard architecture
3. Run tests to verify setup: `pytest`
4. Create first feature branch
5. Make your first commit!
