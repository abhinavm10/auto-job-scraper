"""
Verification utilities for testing the system.

Provides functions for end-to-end testing of the scraper and analyzer.
"""

import asyncio
from sqlmodel import Session, select
from app.db.database import create_db_and_tables, engine
from app.db.models import Company, UserProfile, JobListing
from app.core.scraper import scrape_company


async def verify_system() -> None:
    """
    Runs a verification test of the entire system.
    
    Creates test data, runs the scraper, and displays results.
    """
    print("--- 1. Initialize DB ---")
    create_db_and_tables()
    
    with Session(engine) as session:
        # Check if profile exists
        if not session.get(UserProfile, 1):
            print("Creating dummy profile...")
            profile = UserProfile(
                name="Jane Doe",
                resume_text="Senior Python Developer with 5 years of experience in FastAPI and Machine Learning.",
                preferences="Remote, Python, AI"
            )
            session.add(profile)
            session.commit()
        
        # Add a test company (Use a safe, static-ish site if possible, or a mock)
        # For verification in this environment, we might fail on real network calls if blocked,
        # but let's try a safe known tech blog or documentation site that looks like a list?
        # Actually, let's use a "fake" scraped flow or try a real one.
        # Let's try 'https://quotes.toscrape.com/' as a dummy "career page" to see if it finds links.
        
        if not session.get(Company, 1):
            print("Creating test company...")
            company = Company(name="Test Corp", career_page_url="https://quotes.toscrape.com/")
            # quotes.toscrape has text and links. Our scraper looks for links > 10 chars.
            session.add(company)
            session.commit()
            print(f"Added Company: {company.name}")
        
    print("\n--- 2. Run Scraper ---")
    with Session(engine) as session:
        company = session.get(Company, 1)
        # We run the scrape function directly
        await scrape_company(company)
        
    print("\n--- 3. Check Results ---")
    with Session(engine) as session:
        jobs = session.exec(select(JobListing)).all()
        print(f"Total Jobs Found in DB: {len(jobs)}")
        for job in jobs:
            print(f"- {job.title} (Match: {job.match_score}%)")


if __name__ == "__main__":
    asyncio.run(verify_system())
