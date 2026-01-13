"""
FastAPI application entry point for the Job Auto-Applier system.

This module initializes the FastAPI app, database, and scheduler.
"""

from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from app.db.database import create_db_and_tables
from app.core.scheduler import start_scheduler, run_daily_scan
from app.api.routers import router as api_router


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
