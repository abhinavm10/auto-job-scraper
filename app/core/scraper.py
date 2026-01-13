"""
Web scraper engine using Playwright for career page automation.

Handles browser automation, job link extraction, and deep analysis.
"""

import asyncio
from playwright.async_api import async_playwright
from sqlmodel import Session, select
from datetime import datetime
from app.db.models import Company, JobListing, UserProfile
from app.db.database import get_session, engine
from app.core.analyzer import analyze_job_match, analyze_navigation_step


async def scrape_company(company: Company) -> None:
    """
    Scrapes a single company's career page for job listings.
    
    Args:
        company: The Company model instance to scrape.
    """
    print(f"Starting scrape for {company.name} at {company.career_page_url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set headless=False for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            await page.goto(company.career_page_url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # TODO: Dynamic Navigation (analyze_navigation_step loop) would go here.
            # For Phase 1, we assume the URL might be pre-filtered or we just scrape all.
            
            # Simple Generic Scraper Strategy: Look for <a> tags with 'career', 'job', or simple list items
            # This is heuristic-based.
            
            # Extract links
            job_links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a'));
                return links.map(link => ({
                    text: link.innerText,
                    href: link.href
                })).filter(l => l.href.length > 10);
            }''')
            
            print(f"Found {len(job_links)} potential links.")
            
            session = Session(engine)
            user_profile = session.exec(select(UserProfile)).first()
            if not user_profile:
                print("No user profile found. Skipping analysis.")
                user_profile = UserProfile(resume_text="", preferences="")

            new_jobs = []
            
            for link in job_links:
                # Heuristic: Filter links that look like potential jobs
                # This is weak, but good for a start. Real logic needs more specialized parsing.
                if "job" in link['href'] or "career" in link['href'] or len(link['text']) > 10:
                    
                    # Deduplication
                    existing = session.exec(
                        select(JobListing).where(JobListing.url == link['href'])
                    ).first()
                    if existing:
                        continue
                        
                    print(f"  New Job Found: {link['text']}")
                    
                    # Visit Job Page
                    try:
                        job_page = await context.new_page()
                        await job_page.goto(link['href'])
                        description_text = await job_page.evaluate("document.body.innerText")
                        await job_page.close()
                        
                        # AI Analysis
                        match_result = await analyze_job_match(description_text, user_profile)
                        
                        job = JobListing(
                            title=link['text'][:200],  # Truncate
                            url=link['href'],
                            company_id=company.id,
                            description_text=description_text,
                            match_score=match_result.get('match_score', 0),
                            match_reasoning=match_result.get('reasoning', ''),
                            missing_skills=match_result.get('missing_skills', [])
                        )
                        session.add(job)
                        new_jobs.append(job)
                        
                    except Exception as e:
                        print(f"  Failed to process job link {link['href']}: {e}")

            session.commit()
            
            # Update company last scraped
            company.last_scraped_at = datetime.now()
            session.add(company)
            session.commit()
            session.close()
            
            print(f"Scrape complete for {company.name}. Added {len(new_jobs)} new jobs.")
            
        except Exception as e:
            print(f"Error scraping {company.name}: {e}")
        finally:
            await browser.close()
