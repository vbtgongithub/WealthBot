"""
Seed Dummy Account
==================
Creates a dummy user account for local development and testing.

Usage (pick one):

  # Option A — Backend is running on port 8000:
  python scripts/seed_dummy_account.py

  # Option B — Only database is running (no backend):
  python scripts/seed_dummy_account.py --direct

Dummy credentials:
  Email:    demo@wealthbot.app
  Password: Demo@1234
"""

import argparse
import asyncio
import hashlib
import sys
from decimal import Decimal
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# ── Dummy account details ────────────────────────────────────────────────────
DUMMY_EMAIL = "demo@wealthbot.app"
DUMMY_PASSWORD = "Demo@1234"
DUMMY_FIRST_NAME = "Swarna"
DUMMY_LAST_NAME = "Demo"
DUMMY_MONTHLY_INCOME = Decimal("50000.00")
DUMMY_SAVINGS_GOAL = Decimal("10000.00")
DUMMY_CURRENCY = "INR"


# =============================================================================
# Option A — Via HTTP (requires running backend)
# =============================================================================

def seed_via_api() -> None:
    """Register the dummy account through the REST API."""
    import httpx  # noqa: delay import

    base = "http://localhost:8000"

    payload = {
        "email": DUMMY_EMAIL,
        "password": DUMMY_PASSWORD,
        "first_name": DUMMY_FIRST_NAME,
        "last_name": DUMMY_LAST_NAME,
        "monthly_income": float(DUMMY_MONTHLY_INCOME),
        "savings_goal": float(DUMMY_SAVINGS_GOAL),
        "currency": DUMMY_CURRENCY,
    }

    # 1. Register
    print(f"Registering {DUMMY_EMAIL} via API …")
    try:
        resp = httpx.post(f"{base}/api/v1/auth/register", json=payload, timeout=10)
    except httpx.ConnectError:
        print(
            "ERROR: Could not connect to backend at http://localhost:8000.\n"
            "Start the backend first:\n"
            "  uvicorn app.main:app --reload --port 8000\n"
            "Or use --direct flag to seed via database directly."
        )
        sys.exit(1)

    if resp.status_code == 201:
        print("User created successfully.")
    elif resp.status_code == 409:
        print("User already exists — skipping registration.")
    else:
        print(f"Registration failed ({resp.status_code}): {resp.text}")
        sys.exit(1)

    # 2. Login to verify
    print("Verifying login …")
    resp = httpx.post(
        f"{base}/api/v1/auth/token",
        json={"email": DUMMY_EMAIL, "password": DUMMY_PASSWORD},
        timeout=10,
    )
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print(f"Login successful! Token (first 20 chars): {token[:20]}…")
    else:
        print(f"Login failed ({resp.status_code}): {resp.text}")
        sys.exit(1)

    _print_credentials()


# =============================================================================
# Option B — Direct DB insert (requires only PostgreSQL)
# =============================================================================

async def seed_via_db() -> None:
    """Insert the dummy user directly into the database."""
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    from app.core.config import settings
    from app.core.security import hash_password
    from app.db.models import Base, User

    db_url = settings.database_url
    is_sqlite = db_url.startswith("sqlite")
    display = db_url.split("///")[-1] if is_sqlite else db_url.split("@")[-1]
    print(f"Connecting to database: {display} …")

    kwargs: dict = {"echo": False}
    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}

    engine = create_async_engine(db_url, **kwargs)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables ensured.")

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == DUMMY_EMAIL)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"User {DUMMY_EMAIL} already exists (id={existing.id}) — skipping.")
        else:
            user = User(
                email=DUMMY_EMAIL,
                email_hash=hashlib.sha256(DUMMY_EMAIL.encode()).hexdigest(),
                hashed_password=hash_password(DUMMY_PASSWORD),
                first_name=DUMMY_FIRST_NAME,
                last_name=DUMMY_LAST_NAME,
                monthly_income=DUMMY_MONTHLY_INCOME,
                savings_goal=DUMMY_SAVINGS_GOAL,
                currency=DUMMY_CURRENCY,
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.commit()
            print(f"User created (id={user.id}).")

    await engine.dispose()
    _print_credentials()


# =============================================================================
# Helpers
# =============================================================================

def _print_credentials() -> None:
    print("\n" + "=" * 50)
    print("  DUMMY ACCOUNT CREDENTIALS")
    print("=" * 50)
    print(f"  Email:    {DUMMY_EMAIL}")
    print(f"  Password: {DUMMY_PASSWORD}")
    print("=" * 50)
    print("\nUse these on http://localhost:3000/login\n")


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed a dummy WealthBot account.")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Insert directly into PostgreSQL (skip HTTP API).",
    )
    args = parser.parse_args()

    if args.direct:
        asyncio.run(seed_via_db())
    else:
        seed_via_api()
