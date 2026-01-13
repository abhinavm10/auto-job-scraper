"""
FastAPI application entry point for the Job Auto-Applier system.

This module initializes the FastAPI app, database, and scheduler.
"""

from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from app.db.database import create_db_and_tables
from app.core.scheduler import start_scheduler, run_daily_scan
from app.core.analyzer import get_client
from app.api.routers import router as api_router
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Initializes database and scheduler on startup, handles cleanup on shutdown.
    """
    create_db_and_tables()
    start_scheduler()
    print("Database Initialized & Scheduler Started")
    yield
    print("Shutting down")


app = FastAPI(title="Job Auto Applier", lifespan=lifespan)

# Include all API routes
app.include_router(api_router)


@app.post("/scan-now/")
async def trigger_manual_scan(background_tasks: BackgroundTasks) -> dict:
    """
    Manually trigger a job scan in the background.
    
    Returns:
        A message confirming the scan was triggered.
    """
    background_tasks.add_task(run_daily_scan)
    return {"message": "Scan triggered in background"}


@app.get("/")
def read_root() -> dict:
    """
    Health check endpoint.
    
    Returns:
        A message confirming the application is running.
    """
    return {"message": "Job Auto Applier is running"}


@app.get("/verify")
async def verify_system() -> dict:
    """
    Verify that all system components are working correctly.
    
    Checks:
        - Gemini API key is configured
        - Gemini API connection is working
        - Database is accessible
    
    Returns:
        A status report of all system components.
    """
    status = {
        "overall": "healthy",
        "checks": {
            "api_key_configured": False,
            "gemini_api_working": False,
            "gemini_model": None,
            "database": False,
        },
        "errors": []
    }
    
    # Check 1: API Key configured
    if settings.GEMINI_API_KEY:
        status["checks"]["api_key_configured"] = True
    else:
        status["overall"] = "unhealthy"
        status["errors"].append("GEMINI_API_KEY environment variable is not set")
    
    # Check 2: Test Gemini API connection
    if status["checks"]["api_key_configured"]:
        try:
            client = get_client()
            if client:
                response = await client.aio.models.generate_content(
                    model='gemini-2.0-flash',
                    contents='Respond with exactly: OK',
                    config={'max_output_tokens': 10}
                )
                if response and response.text:
                    status["checks"]["gemini_api_working"] = True
                    status["checks"]["gemini_model"] = "gemini-2.0-flash"
        except Exception as e:
            status["overall"] = "unhealthy"
            status["errors"].append(f"Gemini API error: {str(e)}")
    
    # Check 3: Database connection
    try:
        from sqlmodel import Session, select
        from app.db.database import engine
        from app.db.models import Company
        
        with Session(engine) as session:
            session.exec(select(Company).limit(1)).first()
            status["checks"]["database"] = True
    except Exception as e:
        status["overall"] = "unhealthy"
        status["errors"].append(f"Database error: {str(e)}")
    
    # Final overall status
    all_checks_passed = all(
        v for k, v in status["checks"].items() 
        if k != "gemini_model"  # Skip non-boolean check
    )
    if not all_checks_passed:
        status["overall"] = "unhealthy"
    
    return status
