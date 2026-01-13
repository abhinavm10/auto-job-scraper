"""
Router aggregation module.

Combines all API routers into a single router for easy inclusion in the app.
"""

from fastapi import APIRouter
from app.api.routers.companies import router as companies_router
from app.api.routers.profile import router as profile_router

router = APIRouter()

# Include all sub-routers
router.include_router(companies_router)
router.include_router(profile_router)
