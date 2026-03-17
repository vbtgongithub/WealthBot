"""
WealthBot API v1 Routes
=======================
Version 1 of the WealthBot REST API.
"""

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.assistant import router as assistant_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.statements import router as statements_router
from app.api.v1.transactions import router as transactions_router
from app.api.v1.users import auth_router, users_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(transactions_router)
api_v1_router.include_router(predictions_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(statements_router)
api_v1_router.include_router(assistant_router)
