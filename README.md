# 🏦 WealthBot

> Predictive Personal Finance Application powered by ML

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)

## 📋 Overview

WealthBot is a production-grade personal finance application that leverages machine learning to provide:

- 💰 **Smart Transaction Categorization** using DistilBERT
- 📊 **Predictive Spending Analysis** with XGBoost
- 🛡️ **Safe-to-Spend Calculations** based on your financial goals
- 🔐 **GDPR/SOC 2 Compliant** data handling

## 🏗️ Architecture

```
WealthBot/
├── app/                    # FastAPI Application
│   ├── api/               # API route handlers
│   │   └── v1/           # API version 1
│   ├── core/             # Core configuration & security
│   ├── db/               # Database models & connections
│   ├── schemas/          # Pydantic request/response schemas
│   └── services/         # Business logic & ML integration
├── ml/                    # Machine Learning Lifecycle
│   ├── models/           # Trained model artifacts
│   ├── training/         # Model training pipelines
│   ├── preprocessing/    # Feature engineering
│   └── inference/        # Prediction pipelines
├── alembic/              # Database migrations
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL 16 (or use Docker)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/your-org/wealthbot.git
cd wealthbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Generate a new SECRET_KEY for production
```

### 3. Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

### 4. Run Locally (Development)

```bash
# Start PostgreSQL only
docker-compose up -d db

# Run FastAPI development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API welcome message |
| GET | `/health` | Health check with DB status |
| GET | `/ready` | Kubernetes readiness probe |
| GET | `/live` | Kubernetes liveness probe |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🗃️ Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## 🔒 Security Features

### PII Protection
- Automatic email masking in logs
- SHA-256 hashing for sensitive lookups
- Configurable data retention policies

### Authentication
- JWT-based authentication
- Bcrypt password hashing (12 rounds)
- Configurable token expiration

### GDPR Compliance
- Data consent tracking
- Right to deletion support
- Audit logging ready

## 🤖 ML Models

### XGBoost Spending Predictor
- Predicts monthly spending patterns
- 95% confidence intervals
- Category-level breakdown

### DistilBERT Categorizer
- Automatic transaction categorization
- Confidence scoring
- Continuous learning ready

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.12+) |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 (Async) |
| Validation | Pydantic v2.0 |
| ML - Regression | XGBoost |
| ML - NLP | DistilBERT (Hugging Face) |
| Containers | Docker & Docker Compose |
| Migrations | Alembic |

## 👥 Team

Designed for a two-person team with clear separation between:
- **API Development** (`/app`)
- **ML Engineering** (`/ml`)

## 📝 License

Proprietary - All rights reserved.

---

<p align="center">Made with ❤️ by the WealthBot Team</p>
