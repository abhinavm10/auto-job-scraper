"""
SQLModel database models for the Job Auto-Applier system.

Defines the core data models: Company, JobListing, and UserProfile.
"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, JSON


class Company(SQLModel, table=True):
    """Represents a company whose career page will be monitored."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    career_page_url: str
    is_active: bool = True
    last_scraped_at: Optional[datetime] = None
    
    # Job Listings relationship
    jobs: List["JobListing"] = Relationship(back_populates="company")


class JobListing(SQLModel, table=True):
    """Represents a discovered job listing from a company's career page."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    url: str = Field(unique=True)
    company_id: Optional[int] = Field(default=None, foreign_key="company.id")
    location: Optional[str] = None
    
    # Content
    description_text: Optional[str] = None
    
    # Metadata
    date_found: datetime = Field(default_factory=datetime.now)
    is_active: bool = True  # If the job is still on the site
    
    # AI Analysis
    match_score: Optional[int] = None  # 0-100
    match_reasoning: Optional[str] = None
    missing_skills: Optional[List[str]] = Field(default=None, sa_type=JSON)
    
    company: Optional[Company] = Relationship(back_populates="jobs")


class UserProfile(SQLModel, table=True):
    """Represents the user's profile for job matching."""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = "Default User"
    resume_text: str
    preferences: str  # "Remote, Python, Senior roles only"
