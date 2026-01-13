"""
Job listing API endpoints for viewing scraped job data.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import JobListing, Company

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobListing])
def list_jobs(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    min_score: Optional[int] = Query(None, ge=0, le=100, description="Minimum match score"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    session: Session = Depends(get_session)
) -> List[JobListing]:
    """
    Retrieve job listings with optional filters.
    
    Args:
        company_id: Filter jobs by a specific company.
        min_score: Filter jobs with match score >= this value.
        is_active: Filter by whether the job is still active.
        limit: Maximum number of results to return.
        offset: Number of results to skip (for pagination).
        session: Database session (injected).
    
    Returns:
        List of job listings matching the criteria.
    """
    query = select(JobListing)
    
    if company_id is not None:
        query = query.where(JobListing.company_id == company_id)
    
    if min_score is not None:
        query = query.where(JobListing.match_score >= min_score)
    
    if is_active is not None:
        query = query.where(JobListing.is_active == is_active)
    
    # Order by most recent first
    query = query.order_by(JobListing.date_found.desc())
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    jobs = session.exec(query).all()
    return jobs


@router.get("/stats")
def get_job_stats(session: Session = Depends(get_session)) -> dict:
    """
    Get summary statistics of all scraped jobs.
    
    Returns:
        Statistics including total jobs, active jobs, and score distribution.
    """
    all_jobs = session.exec(select(JobListing)).all()
    
    total = len(all_jobs)
    active = sum(1 for j in all_jobs if j.is_active)
    with_scores = [j for j in all_jobs if j.match_score is not None]
    
    avg_score = None
    if with_scores:
        avg_score = round(sum(j.match_score for j in with_scores) / len(with_scores), 1)
    
    # Score distribution
    high_match = sum(1 for j in with_scores if j.match_score >= 70)
    medium_match = sum(1 for j in with_scores if 40 <= j.match_score < 70)
    low_match = sum(1 for j in with_scores if j.match_score < 40)
    
    return {
        "total_jobs": total,
        "active_jobs": active,
        "analyzed_jobs": len(with_scores),
        "average_match_score": avg_score,
        "score_distribution": {
            "high_match_70_plus": high_match,
            "medium_match_40_69": medium_match,
            "low_match_below_40": low_match
        }
    }


@router.get("/{job_id}", response_model=JobListing)
def get_job(job_id: int, session: Session = Depends(get_session)) -> JobListing:
    """
    Retrieve a specific job listing by ID.
    
    Args:
        job_id: The ID of the job to retrieve.
        session: Database session (injected).
    
    Returns:
        The job listing details.
    
    Raises:
        HTTPException: 404 if job not found.
    """
    job = session.get(JobListing, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/company/{company_id}", response_model=List[JobListing])
def get_jobs_by_company(
    company_id: int,
    session: Session = Depends(get_session)
) -> List[JobListing]:
    """
    Retrieve all job listings for a specific company.
    
    Args:
        company_id: The ID of the company.
        session: Database session (injected).
    
    Returns:
        List of all jobs from the specified company.
    
    Raises:
        HTTPException: 404 if company not found.
    """
    company = session.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    jobs = session.exec(
        select(JobListing)
        .where(JobListing.company_id == company_id)
        .order_by(JobListing.date_found.desc())
    ).all()
    
    return jobs


@router.delete("/{job_id}")
def delete_job(job_id: int, session: Session = Depends(get_session)) -> dict:
    """
    Delete a job listing by ID.
    
    Args:
        job_id: The ID of the job to delete.
        session: Database session (injected).
    
    Returns:
        Confirmation message.
    
    Raises:
        HTTPException: 404 if job not found.
    """
    job = session.get(JobListing, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    session.delete(job)
    session.commit()
    
    return {"message": f"Job {job_id} deleted successfully"}
