# Backend Deployment - Credentials Collection Guide

## Overview

To deploy the RAG chatbot backend, you need 4 pieces of information:

1. **OpenAI API Key**
2. **Neon PostgreSQL Database URL**
3. **Qdrant Vector Database URL**
4. **Qdrant API Key**

---

## Step 1: OpenAI API Key

**How to get it**:
1. Go to https://platform.openai.com/api-keys
2. Log in with your OpenAI account (create one if needed)
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)
5. Save it securely - you won't see it again!

**Format**: `sk-proj-...` (50+ characters)

**What you'll provide**: Your full API key

---

## Step 2: Neon PostgreSQL Database URL

**How to get it**:
1. Go to https://console.neon.tech/
2. Log in or create account
3. Create a new project (or use existing)
4. Click "Connection string"
5. Select "Pooled connection"
6. Copy the full URL that looks like:
   ```
   postgresql+asyncpg://neondb_owner:password@ep-xxxxx.us-west-2.neon.tech/neondb?sslmode=require
   ```

**Format**: `postgresql+asyncpg://user:password@host/database`

**Important**: Use `asyncpg` driver in the URL (not `psycopg2`)

**What you'll provide**: Your full database connection string

---

## Step 3: Qdrant Vector Database Setup

**How to get it**:
1. Go to https://cloud.qdrant.io/
2. Log in or create account
3. Create a new cluster (free tier available)
4. Once created, click on cluster name
5. Go to "API Keys" section
6. Create a new API key (copy the full key)
7. Go to "Overview" to get cluster URL (https://xxx-yyy-zzz.qdrant.io)

**Format for URL**: `https://xxxxx.qdrant.io` (HTTPS required)

**Format for API Key**: Long alphanumeric string

**What you'll provide**:
- Qdrant URL (cluster endpoint)
- Qdrant API Key

---

## Step 4: Collect Your Values

Once you have all credentials, provide them in this format:

```
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key-here
```

---

## Security Notes ⚠️

- ✅ Never commit `.env` file to Git (it's in `.gitignore`)
- ✅ Keep API keys private - don't share in PRs or public channels
- ✅ Rotate keys if you accidentally expose them
- ✅ Use environment-specific keys for dev vs. production

---

## Next Steps

Once you have the 4 credentials above, I will:

1. Create `.env` file in `backend/` directory
2. Populate all required variables
3. Verify environment loading works
4. Initialize the database schema
5. Set up Qdrant collection
6. Start the FastAPI backend
7. Ingest the 20 textbook chapters
8. Validate the RAG pipeline

**Ready?** Provide your credentials and we'll proceed!
