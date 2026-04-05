# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Reference

**Project:** WealthBot — AI-powered predictive personal finance app for Indian students
**Stack:** FastAPI (Python 3.12) + PostgreSQL 18 + Next.js 16 + XGBoost/DistilBERT (ONNX)
**Deliverable:** ML-predicted "Safe-to-Spend" daily spending limit

## Commands

```bash
# Backend
uvicorn app.main:app --reload --port 8000
pytest --cov=app --cov-report=term-missing
pytest -k test_name -v                    # Single test
black app/ ml/ tests/ && ruff check app/ ml/ tests/ && mypy app/
alembic upgrade head                      # Migrations

# Frontend
cd frontend && npm run dev                # :3000
npm run lint && npm run type-check

# E2E
cd frontend && npx playwright test        # 36 smoke tests

# Docker
docker-compose up --build                 # Full stack
```

## Architecture

```
Backend (FastAPI)           Frontend (Next.js 16)      ML Pipeline
app/main.py (entry)         src/app/ (pages)           ml/inference/
app/api/v1/ (routes)        src/components/            ml/preprocessing/
app/core/ (config,security) src/hooks/useApi.ts        ml/training/
app/db/ (models,database)   src/stores/ (Zustand)      ml/models/ (ONNX)
app/services/ml_service.py  src/lib/api.ts (Axios)
```

**Key patterns:**
- **DB:** Async SQLAlchemy 2.0, `Numeric(15,2)` for money (never Float)
- **Auth:** JWT (30min access, 7d refresh), bcrypt, PII masking
- **ML:** ONNX Runtime only, wrap in `run_in_threadpool()` for async
- **State:** React Query (server), Zustand (UI only), token in localStorage

## Critical Constraints

| Area | Rule |
|------|------|
| ML inference | Never call `model.predict()` in async — use `run_in_threadpool()` |
| Financial | `Numeric(15,2)` in DB, `Decimal` in Python, `float` only for JSON |
| Frontend | `'use client'` only on interactive leaves, not pages/layouts |
| API hooks | Gate with `enabled: !!getToken()` to prevent 401 spam |
| Cold-start | `MIN_TRANSACTIONS_FOR_ML = 10` — below uses heuristic |

## Code Style

**Python:** Black (88), Ruff (E,W,F,I,B,C4,UP,ARG,SIM), MyPy strict, Google docstrings
**TypeScript:** Strict, `@/*` alias, Tailwind only, lucide-react icons

## Environment

```
Demo: student@wealthbot.in / SecureDemo!2026 (7,416 transactions)
DB:   wealthbot_db (dev), wealthbot_test (test)
Env:  DATABASE_URL, SECRET_KEY (required), REDIS_URL (optional)
```

## Known Gotchas

1. `User.currency` ORM default="USD", schema default="INR"
2. Sidebar "Analytics"→`/budgets`, "Settings"→`/investments` (intentional)
3. AI chat is rule-based (keyword matching), not LLM
4. Tests require real PostgreSQL (no SQLite)
5. ONNX models in `.gitignore` — training artifacts

## References

- `.github/copilot-instructions.md` — Phase roadmap, session state
- `README.md` — Features, quick start, API reference
