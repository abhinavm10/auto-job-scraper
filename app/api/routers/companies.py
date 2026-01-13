"""
Company API endpoints for managing monitored companies.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import Company

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("/", response_model=Company)
def create_company(
    company: Company, 
    session: Session = Depends(get_session)
) -> Company:
    """
    Create a new company to monitor for job listings.
    
    Args:
        company: The company data to create.
        session: Database session (injected).
    
    Returns:
        The created company with its assigned ID.
    """
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


@router.get("/", response_model=list[Company])
def read_companies(session: Session = Depends(get_session)) -> list[Company]:
    """
    Retrieve all monitored companies.
    
    Args:
        session: Database session (injected).
    
    Returns:
        List of all companies in the database.
    """
    companies = session.exec(select(Company)).all()
    return companies
