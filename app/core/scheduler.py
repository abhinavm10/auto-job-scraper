"""
Background job scheduler using APScheduler.

Manages the daily scan job that checks all active companies for new listings.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select
from datetime import datetime
from app.db.database import engine
from app.db.models import Company
from app.core.scraper import scrape_company

scheduler = AsyncIOScheduler()


async def run_daily_scan() -> None:
    """
    Runs the daily job scan for all active companies.
    
    Iterates through all active companies and scrapes their career pages
    sequentially to avoid overloading local resources.
    """
    print(f"Running Daily Scan at {datetime.now()}")
    with Session(engine) as session:
        companies = session.exec(
            select(Company).where(Company.is_active == True)
        ).all()
        for company in companies:
            # We run sequentially to avoid overloading local resources,
            # but this could be parallelized with asyncio.gather
            await scrape_company(company)
    print("Daily Scan Complete")


def start_scheduler() -> None:
    """
    Starts the APScheduler with a 24-hour interval job.
    
    The scheduler runs the daily scan every 24 hours.
    """
    scheduler.add_job(run_daily_scan, 'interval', hours=24)
    # scheduler.add_job(run_daily_scan, 'date')  # Run immediately on start for testing?
    scheduler.start()
