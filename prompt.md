# WealthBot Foundation Architect Prompt

### Role & Objective
Act as a **Principal Software Architect** and **Lead ML Engineer**. Your objective is to initialize a production-grade repository for **WealthBot**, a predictive personal finance application.

### Tech Stack Specifications
* **Backend:** FastAPI (Python 3.12+)
* **Database:** PostgreSQL with SQLAlchemy 2.0 (Async) and Pydantic v2.0
* **AI/ML:** XGBoost (Regression) and DistilBERT (via Hugging Face)
* **Infrastructure:** Docker & Docker-Compose

### Task Requirements

#### 1. Modular Directory Structure
Generate a complete file architecture optimized for a two-person team. Ensure clear separation between the **API logic (`/app`)** and the **Machine Learning lifecycle (`/ml`)**.

#### 2. Boilerplate Implementation
Provide robust, error-free code for the following foundational files:
* **`app/main.py`**: Entry point featuring health checks, project metadata, and CORS middleware.
* **`app/db/database.py`**: Async PostgreSQL connection logic using an `async_sessionmaker` and the Singleton pattern for the engine.
* **`app/db/models.py`**: SQLAlchemy models for `Users` and `Transactions`. The `amount` column MUST use the `Numeric(15,2)` type for financial precision.
* **`Dockerfile` & `docker-compose.yml`**: Configuration to orchestrate the FastAPI application and a PostgreSQL 16 container.
* **`requirements.txt`**: A comprehensive list of modern libraries (e.g., `uvicorn`, `sqlalchemy`, `psycopg3`, `python-dotenv`, `xgboost`, `transformers`).

#### 3. Integration Service
Create a placeholder service in `app/services/ml_service.py`. This should demonstrate how the FastAPI layer will asynchronously load an XGBoost model artifact (via `joblib` or `pickle`) and perform a "Safe-to-Spend" calculation based on user transaction history.

#### 4. Environment Template
Provide a `.env.example` file containing necessary keys for `DATABASE_URL`, `SECRET_KEY`, and `MODEL_PATH`.

### Constraints & Standards
* **Type Hinting:** All functions must include Python type hints for clarity and validation.
* **Clean Code:** Follow PEP 8 standards and prioritize readability.
* **Security:** Ensure the architecture includes a clear strategy for data masking and PII protection to satisfy GDPR/SOC 2 standards.

### Output Style
The response should be highly organized, utilizing clear headings and code blocks. Provide brief explanations for architectural decisions made.
