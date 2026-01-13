"""
Database connection and session management.

Provides SQLModel engine creation and session dependency for FastAPI.
"""

from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Import models to ensure they're registered with SQLModel metadata
from app.db.models import Company, JobListing, UserProfile  # noqa: F401

engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables() -> None:
    """Create all database tables defined in SQLModel models."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    FastAPI dependency that yields a database session.
    
    Yields:
        Session: A SQLModel session for database operations.
    """
    with Session(engine) as session:
        yield session
