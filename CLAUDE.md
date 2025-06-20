# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# 🧠 Donkey Workspace / MythOS — Claude Developer Guide

This is **MythOS** (aka Donkey Workspace), a sophisticated Django-based AI assistant ecosystem with memory-aware agents, symbolic reflection systems, and recursive self-documentation capabilities.

---

## 🚀 Quick Start Commands

### Backend Development
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations && python manage.py migrate
make run                    # Starts Redis + Django + Celery
python manage.py runserver  # Django only
```

### Frontend Development  
```bash
cd frontend
npm install
npm run dev                 # Vite dev server on port 5173
```

### Full Stack Development
```bash
make full-dev              # Runs backend and frontend concurrently
docker-compose up --build  # Full Docker stack
```

### Testing
```bash
# Backend tests
cd backend
./tests/run_tests.sh       # Runs migrations + pytest
pytest --cov              # With coverage

# Frontend tests
cd frontend
npm test                   # Runs comprehensive test suite
npm run lint              # ESLint
```

---

## 🏗️ Project Architecture

### Core Structure
```
donkey_workspace/
├── backend/               # Django REST API
│   ├── assistants/       # Core AI assistant models & logic
│   ├── memory/           # Memory chains, entries, reflections  
│   ├── mcp_core/         # Orchestration & context protocol
│   ├── intel_core/       # Document ingestion & search
│   ├── embeddings/       # Vector embedding pipeline
│   ├── prompts/          # Reusable system prompt templates
│   ├── agents/           # Agent clusters & orchestration
│   ├── characters/       # Character profiles & similarity
│   └── server/           # Django settings & config
├── frontend/             # React + Vite UI
├── docs/                 # Developer documentation
│   ├── core/            # Active documentation
│   └── archive/         # Deprecated docs
└── scripts/              # Deployment & utility scripts
```

### Key Technologies
- **Backend**: Django 5.2, DRF, PostgreSQL with pgvector, Redis, Celery
- **Frontend**: React 19, Vite, Bootstrap 5, React Router v7
- **AI/ML**: OpenAI API, LiteLLM, sentence-transformers, embeddings
- **Infrastructure**: Docker, GitHub Actions CI/CD, Sentry monitoring

---

## 🤖 Core System Concepts

### Assistants
- **Purpose**: Memory-aware AI agents that chat, reflect, and evolve
- **Capabilities**: Project management, memory chains, sub-assistant spawning
- **Architecture**: Split across `AssistantIdentity`, `AssistantConfiguration` models
- **Key Files**: `backend/assistants/`, `AGENTS.md`

### Memory System  
- **Components**: Memory entries, chains, reflections, symbolic anchors
- **Features**: RAG-based retrieval, glossary mutation, drift tracking
- **Commands**: `python manage.py reflect_on_document`, `mutate_glossary_anchors`

### Document Intelligence
- **Pipeline**: PDF upload → chunking → embedding → search
- **Models**: `Document`, `DocumentChunk`, `DocumentProgress`
- **Debugging**: RAG failure logs, embedding audit reports

### Prompt Engineering
- **System**: Reusable templates, mutation tracking, version control
- **Commands**: `ingest_prompts`, `reembed_all_prompts`

---

## 🛠️ Development Commands

### Database Management
```bash
# Reset database completely
make reset-db              # Drops/recreates DB + migrations

# Migrate and seed data
python manage.py migrate
make seed-all              # Runs all seeders
./scripts/seed_all.sh      # Alternative seeding script
```

### Data Seeding
```bash
# Individual seeders
python manage.py seed_assistants
python manage.py seed_memory_entries  
python manage.py seed_dev_docs
python manage.py seed_demo_sessions

# Bulk operations
make run-all-scripts       # All management commands + dev scripts
```

### Embedding & RAG Management
```bash
# Fix embedding issues
python manage.py fix_embeddings_status
python manage.py backfill_missing_embeddings
python manage.py reembed_document --doc-id=<uuid>

# RAG diagnostics
python manage.py run_rag_tests --assistant <slug>
python manage.py inspect_rag_failure --doc <uuid>
python manage.py generate_diagnostic_reports
```

### Reflection & Memory
```bash
# Reflection operations
python manage.py reflect_on_document --doc <uuid> --assistant <slug>
python manage.py retry_birth_reflection --all
python manage.py replay_reflections

# Glossary & anchor management  
python manage.py infer_glossary_anchors --assistant <slug>
python manage.py validate_anchors
python manage.py track_anchor_drift
```

### Development Utilities
```bash
# Codex operations
make codex                 # Run codex helpers
make codex-dry            # Dry run mode

# Process management
make kill                 # Kill all dev processes
make restart              # Kill + restart everything
make safe-restart         # Graceful restart with flush

# Linting & formatting
make format               # Black formatter
make lint                 # Backend + frontend linting
```

---

## 🧪 Testing Strategy

### Backend Testing
- **Location**: `backend/tests/`
- **Runner**: pytest with Django integration
- **Coverage**: 80%+ requirement, reports in `htmlcov/`
- **Command**: `./tests/run_tests.sh` (handles migrations automatically)

### Frontend Testing  
- **Framework**: Custom test runners for React components
- **Files**: `*.test.js` alongside components
- **Command**: `npm test` (runs comprehensive suite)
- **E2E**: Cypress tests in `cypress/e2e/`

### CI/CD Pipeline
- **GitHub Actions**: `.github/workflows/ci.yml`
- **Services**: PostgreSQL 15, Redis 7 in CI
- **Checks**: Linting (black, flake8, eslint), tests, security
- **Deployment**: Automated on main branch

---

## 🔧 Configuration & Environment

### Environment Variables
```bash
# Required for development
SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=donkey
DB_USER=postgres  
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/1

# Optional integrations
SENTRY_DSN=your-sentry-dsn
OPENAI_API_KEY=your-openai-key
VITE_API_URL=http://localhost:8000/api
```

### Docker Configuration
- **Services**: PostgreSQL, Redis, Backend, Frontend
- **Ports**: Backend (8000), Frontend (5173), DB (5432), Redis (6379)
- **Volumes**: Persistent PostgreSQL data, source code mounting

---

## 📚 Key Documentation Files

### Essential Reading
- `README.md` - Project overview & getting started
- `AGENTS.md` - Codex agent development protocols  
- `MANAGEMENT_COMMANDS.md` - CLI command reference
- `PHASE_SUMMARY.md` - Development phase history
- `MYTHOS_YEAR_ONE_REVIEW.md` - Project evolution narrative

### API Documentation
- `docs/api_overview.md` - REST endpoint reference
- `docs/SystemOverview.md` - Architecture deep dive
- Generated API docs at `/api/schema/swagger/` when running

### Specialized Guides
- `docs/MAINTENANCE.md` - Production maintenance runbook
- `docs/ROADMAP.md` - Current priorities & experiments
- `docs/How-To-Docs/` - Troubleshooting guides

---

## 🎯 Development Workflow

### Code Style & Standards
- **Python**: Black formatting, flake8 linting, type hints preferred
- **JavaScript**: ESLint, Prettier, modern React patterns
- **CSS**: Tailwind CSS utility classes, Bootstrap 5 components
- **Documentation**: Concise docstrings, inline comments for complexity

### Git Workflow
- **Main branch**: `main` (protected, requires PR)
- **Features**: Feature branches, squash merge preferred
- **Commits**: Descriptive messages, reference issues when applicable

### Security & Performance
- **Authentication**: JWT tokens via `/api/token/`
- **Rate limiting**: 20/min anonymous, 200/min authenticated  
- **Headers**: CSP, X-Frame-Options, security headers configured
- **Monitoring**: Sentry error tracking, Prometheus metrics at `/metrics/`

---

## 🚨 Common Issues & Solutions

### Database Issues
```bash
# Migration conflicts
python manage.py migrate --fake-initial
python manage.py makemigrations --merge

# Fresh start
make reset-db && make seed-all
```

### Embedding Pipeline Issues  
```bash
# Stuck embeddings
python manage.py check_embedding_status
python manage.py fix_embeddings_status

# Celery not running (sync fallback)
export FORCE_EMBED_SYNC=True
```

### Frontend Development
```bash
# Module resolution issues
rm -rf node_modules package-lock.json
npm install

# API connection issues
# Check VITE_API_URL in .env
```

---

## 🎪 Demo & Testing Data

### Demo Assistant Flows
```bash
python manage.py seed_demos
# Visit: /assistants/prompt_pal/demo_recap/<session_id>/
#        /assistants/prompt_pal/demo_overlay/
#        /assistants/prompt_pal/demo_replay/<session_id>/
```

### Performance Benchmarking
```bash
./scripts/benchmark_endpoints.sh  # Results in benchmark_results.json
```

### Load Testing
```bash
# With locust (load_tests/locustfile.py)
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🧠 AI Assistant System

### Active Assistants
- **DonkGPT**: General memory-aware assistant
- **Recurra**: Symbolic processing & contradiction resolution
- **Zeno**: DevOps & task automation  
- **ClarityBot**: RAG diagnostics & system health
- **Prompt Pal**: Demo assistant for onboarding

### Memory & Reflection Architecture
- **Memory Chains**: Linked memory entries with context
- **Symbolic Anchors**: Glossary terms with mutation tracking
- **Reflection Logs**: Assistant self-analysis and learning
- **RAG Pipeline**: Document chunks → embeddings → similarity search

---

## 📋 Claude AI Expectations

When working with this codebase:

1. **Understand the Domain**: This is a complex AI system with recursive self-improvement
2. **Use Management Commands**: Extensive CLI tools available - check `MANAGEMENT_COMMANDS.md`
3. **Follow Phase Planning**: Development follows structured phases - see `PHASE_SUMMARY.md`
4. **Test Thoroughly**: High test coverage expected, use provided test runners
5. **Document Changes**: Update relevant `.md` files, especially for new features
6. **Security Aware**: Handle authentication, validate inputs, respect rate limits
7. **Performance Conscious**: Large datasets, async operations, caching strategies important

### Development Principles
- **Recursive Self-Documentation**: System documents and reflects on itself
- **Symbolic Processing**: Heavy use of semantic embeddings and similarity
- **Memory-Aware**: All assistants maintain context and learn from interactions  
- **Modular Architecture**: Clean separation between apps and concerns
- **Evolution-Friendly**: Built to adapt and grow over time

---

*This guide serves as your compass for navigating the MythOS codebase. When in doubt, consult the extensive documentation in `/docs/` or run management commands to explore the system state.*