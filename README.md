# 🏦 WealthBot

> AI-powered predictive personal finance app for Indian students — predicts a **"Safe-to-Spend"** daily limit

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/Next.js-16-black.svg)](https://nextjs.org/)
[![PostgreSQL 18](https://img.shields.io/badge/PostgreSQL-18-336791.svg)](https://www.postgresql.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-ONNX-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 📋 Overview

WealthBot is a production-grade personal finance app built for **Indian students** managing ₹ budgets across UPI apps like GPay, PhonePe, and merchants like Swiggy, Zomato, Zepto, and Rapido.

### Key Features

- 💰 **Safe-to-Spend** — ML-predicted daily spending limit that adapts to your habits
- 🏷️ **Smart Categorization** — DistilBERT auto-classifies transactions into 17 categories (~5ms ONNX inference)
- 📊 **Spending Predictions** — XGBoost forecasts next-7-day spending with confidence intervals
- 🔍 **Transaction Search** — Full-text search across merchants, descriptions, and categories
- 🤖 **Aura AI Assistant** — Contextual financial tips integrated into every page
- 🔐 **Privacy First** — GDPR/SOC 2 compliant PII masking (email, phone, PAN, Aadhaar, UPI VPA)
- 📱 **Responsive** — Fully tested at mobile (375px), tablet (768px), and desktop (1440px)

### Screenshots

| Dashboard | Transactions | Mobile |
|:---------:|:------------:|:------:|
| Dark-themed gauge + metrics | Search, paginate, inline category edit | Hamburger nav + collapsible Aura |

## 🏗️ Architecture

```
Backend (FastAPI)              Frontend (Next.js 16)        ML Pipeline
├── app/main.py (entry)        ├── src/app/ (pages)         ├── ml/inference/
│   ├── Lifespan: DB + ML     │   ├── page.tsx (home)      │   ├── predictor.py
│   ├── CORS middleware        │   ├── login/               │   └── categorizer.py
│   └── Health/readiness       │   ├── transactions/        ├── ml/preprocessing/
├── app/api/v1/ (routes)       │   ├── budgets/             │   ├── features.py (21 features)
│   ├── users.py (auth+CRUD)   │   └── investments/         │   └── synthetic_data.py
│   ├── transactions.py        ├── src/components/          ├── ml/training/
│   └── predictions.py         │   ├── layout/ (3-col)      │   ├── train_xgboost.py
├── app/core/                  │   ├── ui/ (MetricCard…)    │   └── train_categorizer.py
│   ├── config.py (Settings)   │   ├── charts/ (Recharts)   └── ml/models/ (artifacts)
│   └── security.py (JWT+PII)  │   ├── assistant/ (Aura)        ├── feature_config.json
├── app/db/                    │   └── providers/                ├── xgboost_spending.onnx
│   ├── database.py (async)    ├── src/hooks/useApi.ts           ├── categorizer.onnx
│   └── models.py              ├── src/stores/ (Zustand)         └── label_encoder.json
├── app/schemas/ (Pydantic)    ├── src/lib/api.ts (Axios)
└── app/services/ml_service.py └── src/types/index.ts
```

### Data Flow

```
User Action → Next.js (React Query) → /api/* rewrite → FastAPI /api/v1/*
                                                            │
                                          ┌─────────────────┼─────────────────┐
                                          ▼                 ▼                 ▼
                                    PostgreSQL 18    ONNX Runtime       Heuristic
                                    (async SQLAlchemy)  (XGBoost +     (cold-start
                                                        DistilBERT)     fallback)
```

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Node.js | LTS (20+) |
| PostgreSQL | 18 (or use Docker) |
| Docker | Optional — for containerized setup |

### 1. Clone & Setup

```bash
git clone https://github.com/vbtgongithub/WealthBot.git
cd WealthBot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
cp .env.example .env
# Edit .env — at minimum set DATABASE_URL and SECRET_KEY
# Generate a secure secret key with: openssl rand -hex 32
```

### 3. Database Setup

```bash
# Option A: Docker (recommended)
docker-compose up -d db

# Option B: Local PostgreSQL
# Create DB + user, then run:
psql -U wealthbot_user -d wealthbot_db -f scripts/init-db.sql

# Run migrations
alembic upgrade head

# (Optional) Seed demo data
python scripts/seed_dummy_account.py
```

### 4. Start Backend

```bash
uvicorn app.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```

### 6. Docker Compose (All Services)

```bash
docker-compose up --build
# Services: db (PostgreSQL 18), api (FastAPI :8000), redis (Redis 7 :6379)
```

## 📡 API Reference

All endpoints under `/api/v1/` require JWT Bearer authentication unless noted.

### Health & System

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/` | No | API welcome message |
| GET | `/health` | No | Health check with DB connectivity status |
| GET | `/docs` | No | Swagger UI interactive documentation |
| GET | `/redoc` | No | ReDoc API documentation |

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| POST | `/api/v1/auth/register` | No | Create a new user account |
| POST | `/api/v1/auth/token` | No | Login — returns JWT access token |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/api/v1/users/me` | Yes | Get current user profile |
| PUT | `/api/v1/users/me` | Yes | Update profile (name, income, savings goal) |

### Transactions

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/api/v1/transactions` | Yes | List transactions (paginated, searchable) |
| POST | `/api/v1/transactions` | Yes | Create a new transaction |
| GET | `/api/v1/transactions/{id}` | Yes | Get single transaction |
| PUT | `/api/v1/transactions/{id}` | Yes | Update a transaction |
| PATCH | `/api/v1/transactions/{id}/category` | Yes | Update category only |
| DELETE | `/api/v1/transactions/{id}` | Yes | Delete a transaction |

### Predictions (ML)

| Method | Endpoint | Auth | Description |
|--------|----------|:----:|-------------|
| GET | `/api/v1/safe-to-spend` | Yes | Daily safe-to-spend with risk level |

> **Cold-start:** Users with < 10 transactions get heuristic predictions (`model_used: "heuristic"`). Once threshold is met, XGBoost activates (`model_used: "xgboost"`).

## 🎨 Frontend (Aura.fi)

Dark-themed financial dashboard built with **Next.js 16 App Router** + **Tailwind CSS**.

### Pages

| Page | Route | Status | Description |
|------|-------|:------:|-------------|
| Login | `/login` | ✅ Live | Login / register toggle, auto-login after registration |
| Dashboard | `/` | ✅ Live | Safe-to-spend gauge, recent transactions, metric cards |
| Transactions | `/transactions` | ✅ Live | Search (300ms debounce), pagination, inline category edit |
| Analytics | `/budgets` | 🔜 Mock | Spending velocity, subscription detection |
| Settings | `/investments` | 🔜 Mock | Statement upload, privacy controls |

### State Management

| Layer | Tool | Purpose |
|-------|------|---------|
| Server state | React Query (`@tanstack/react-query`) | API caching, loading states, optimistic updates |
| Client state | Zustand | UI toggles (sidebar, dark mode) — never syncs API data |

### Component Library

| Component | Description |
|-----------|-------------|
| `MainLayout` | 3-column responsive layout (sidebar / main / Aura) |
| `Sidebar` | Fixed left nav, slide-in hamburger on mobile |
| `Header` | Page title, notification bell, action button |
| `AuraAssistant` | Right-side AI chat panel with contextual tips |
| `MetricCard` | Stat card with icon, value, and trend indicator |
| `CategoryBadge` | Color-coded category tag |
| `ProgressBar` | Animated progress indicator |
| `BudgetGauge` | Circular gauge for safe-to-spend visualization |

### Design Tokens

| Token | Value |
|-------|-------|
| Background | `#0a0f1a` (primary), `#0f1629` (secondary), `#141b2d` (card) |
| Accent | `#22c55e` (green), `#16a34a` (dark), `#4ade80` (light) |
| Font | Inter, system-ui, sans-serif |
| Icons | `lucide-react` exclusively |

## 🤖 ML Pipeline

### Architecture Overview

```
Synthetic Data → Feature Engineering → Training (Colab T4) → ONNX Export
     │                  │                                         │
     ▼                  ▼                                         ▼
14k Indian-student   21-feature vector              xgboost_spending.onnx
transactions         (feature_config.json)          categorizer.onnx
(100 users × 2mo)                                   tokenizer/ + label_encoder.json
                                                          │
                                                          ▼
                                              ONNX Runtime (CPU, 16GB)
                                              Loaded at FastAPI startup
                                              Shared across requests
```

### Models

| Model | Task | Input | Output | Inference |
|-------|------|-------|--------|-----------|
| **XGBoost** | 7-day spending prediction | 21-feature vector | `(prediction, lower_ci, upper_ci)` | ~1ms ONNX |
| **DistilBERT** | Transaction categorization | `merchant + description` text | `(category, confidence)` across 17 labels | ~5ms ONNX |

### 21-Feature Vector

Temporal (5): `day_of_month`, `day_of_week`, `is_weekend`, `days_until_month_end`, `is_salary_week`

Spending (6): `total_spending_7d`, `total_spending_30d`, `avg_daily_spending_7d`, `avg_daily_spending_30d`, `max_single_txn_7d`, `txn_count_7d`

Category ratios (6): `food_ratio`, `transport_ratio`, `shopping_ratio`, `entertainment_ratio`, `utilities_ratio`, `essential_ratio`

Financial context (4): `monthly_income`, `savings_goal_ratio`, `recurring_expense_ratio`, `income_spent_ratio`

### Heuristic Fallback

If ONNX models are missing at startup, all prediction endpoints gracefully fall back to rule-based logic. The Safe-to-Spend formula:

```
daily_allowance = max(0, (monthly_income − savings_goal − month_expenses) / days_remaining)
```

Risk levels: `low` (> 40% budget remaining), `medium` (20–40%), `high` (< 20%).

## 🔒 Security

### Authentication
- **JWT** (HS256) with 30-minute expiry — payload: `sub`, `exp`, `iat`, `type`
- **bcrypt** password hashing (12 rounds) via passlib
- Bearer token stored in `localStorage` (`auth_token` key)
- Axios interceptor handles 401 → `/login` redirect

### PII Masking (GDPR/SOC 2)
- Regex-based redaction for: email, phone, SSN, credit card, **Indian PAN, Aadhaar, UPI VPAs**
- `sanitize_log_data()` recursively redacts all sensitive fields
- Controlled by `ENABLE_PII_MASKING` environment variable

### Infrastructure
- CORS whitelist via `ALLOWED_ORIGINS`
- Docker: non-root `wealthbot` user (UID 1000), read-only volume mounts
- PostgreSQL extensions: `uuid-ossp` (UUID generation), `pg_trgm` (fuzzy text search)

## 🧪 Testing

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Lint & format
black app/ ml/ tests/
ruff check app/ ml/ tests/
mypy app/

# Frontend checks
cd frontend
npm run lint          # ESLint
npm run type-check    # tsc --noEmit
```

**Test database:** SQLite in-memory with `StaticPool` for fast async tests (see `tests/conftest.py`).

## 🗃️ Database

### Schema

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `users` | UUID PK, email (unique), `monthly_income` Numeric(15,2), `savings_goal` Numeric(15,2) | Financial amounts always Numeric, never Float |
| `transactions` | UUID PK, FK → users, `amount` Numeric(15,2), `category`, `merchant_name`, `is_recurring` | `predicted_category` + `category_confidence` for ML results |

### Migrations

```bash
alembic upgrade head                              # Apply all migrations
alembic revision --autogenerate -m "description"  # Create new migration
alembic downgrade -1                              # Rollback one version
```

Alembic auto-formats migrations with Black post-write hook.

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI 0.109+ · Python 3.12 · Pydantic v2 · Async SQLAlchemy 2.0 |
| **Frontend** | Next.js 16 · React 18 · Tailwind CSS 3.4 · Zustand · React Query 5 |
| **Database** | PostgreSQL 18 · asyncpg · Alembic |
| **ML Training** | XGBoost · DistilBERT (HuggingFace) · PyTorch · scikit-learn |
| **ML Inference** | ONNX Runtime (CPU) |
| **Charts** | Recharts |
| **Infrastructure** | Docker (multi-stage) · Docker Compose · Redis 7 |

## 📁 Project Structure

```
WealthBot/
├── app/                        # FastAPI backend
│   ├── main.py                 # Entry point, lifespan, CORS
│   ├── api/v1/                 # Route handlers (users, transactions, predictions)
│   ├── core/                   # Config (pydantic-settings), security (JWT, PII)
│   ├── db/                     # SQLAlchemy models, async DatabaseManager
│   ├── schemas/                # Pydantic request/response schemas
│   └── services/               # MLService singleton (ONNX model management)
├── frontend/                   # Next.js 16 App Router
│   └── src/
│       ├── app/                # Pages (login, home, transactions, budgets, investments)
│       ├── components/         # layout/, ui/, charts/, assistant/, providers/
│       ├── hooks/              # useApi.ts (React Query hooks), useAuth.ts
│       ├── stores/             # Zustand (UI state only)
│       ├── lib/                # api.ts (Axios instance), utils.ts
│       ├── constants/          # data.ts (mock data, types)
│       └── types/              # TypeScript interfaces
├── ml/                         # Machine Learning pipeline
│   ├── models/                 # Artifacts (ONNX, tokenizer, feature config)
│   ├── preprocessing/          # Feature engineering, synthetic data generation
│   ├── training/               # XGBoost + DistilBERT training scripts (Colab-compatible)
│   └── inference/              # ONNX inference wrappers
├── alembic/                    # Database migrations
├── scripts/                    # init-db.sql, seed_dummy_account.py
├── tests/                      # pytest suite (async, SQLite in-memory)
├── docker-compose.yml          # PostgreSQL 18 + FastAPI + Redis 7
├── Dockerfile                  # Multi-stage (builder → runtime), non-root user
├── requirements.txt            # Python dependencies
└── .env.example                # Environment variable template
```

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...@localhost:5432/wealthbot_db` | Async PostgreSQL connection |
| `SECRET_KEY` | *(none — must be set)* | JWT signing key (**required**) |
| `APP_ENV` | `development` | Environment name |
| `DEBUG` | `true` | Debug mode toggle |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `MODEL_PATH` | `./ml/models/xgboost_spending_model.pkl` | XGBoost model artifact path |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | CORS allowed origins (comma-separated) |
| `ENABLE_PII_MASKING` | `true` | Toggle PII redaction in logs |

## 🗺️ Roadmap

- [x] **Phase 1** — Backend API (auth, transactions, predictions, migrations)
- [x] **Phase 2** — Frontend wiring (login, dashboard, transactions, React Query)
- [x] **Phase 2.5** — Visual testing & responsiveness (3 breakpoints)
- [x] **Phase 3A** — Data foundation (synthetic data, feature engineering)
- [ ] **Phase 3B** — Model training (XGBoost + DistilBERT → ONNX export)
- [ ] **Phase 3C** — Inference integration (ONNX wrappers, MLService refactor)
- [ ] **Phase 3D** — Config & verification (end-to-end ML pipeline)
- [ ] **Phase 4** — Hardening (test suite ≥80% coverage, rate limiting, structured logging)

## 📝 License

Proprietary — All rights reserved.

---

<p align="center">Made with ❤️ by the WealthBot Team</p>
