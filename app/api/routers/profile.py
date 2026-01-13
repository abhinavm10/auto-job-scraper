"""
User profile API endpoints for managing the user's resume and preferences.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db.database import get_session
from app.db.models import UserProfile

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/", response_model=UserProfile)
def update_profile(
    profile: UserProfile, 
    session: Session = Depends(get_session)
) -> UserProfile:
    """
    Create or update the user's profile.
    
    For simplicity, assumes a single user. If a profile exists, it will be updated.
    Otherwise, a new profile is created.
    
    Args:
        profile: The profile data to create or update.
        session: Database session (injected).
    
    Returns:
        The created or updated user profile.
    """
    existing = session.exec(select(UserProfile)).first()
    if existing:
        existing.name = profile.name
        existing.resume_text = profile.resume_text
        existing.preferences = profile.preferences
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    else:
        session.add(profile)
        session.commit()
        session.refresh(profile)
        return profile


@router.get("/", response_model=UserProfile)
def get_profile(session: Session = Depends(get_session)) -> UserProfile:
    """
    Retrieve the current user's profile.
    
    Args:
        session: Database session (injected).
    
    Returns:
        The user's profile.
    
    Raises:
        HTTPException: 404 if no profile has been set.
    """
    profile = session.exec(select(UserProfile)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not set")
    return profile
