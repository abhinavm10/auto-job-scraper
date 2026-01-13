"""
Database connection and session management.

Provides SQLModel engine creation and session dependency for FastAPI.
Supports both SQLite (local development) and PostgreSQL (production).
"""

from sqlmodel import SQLModel, create_engine, Session
from app.config import settings

# Import models to ensure they're registered with SQLModel metadata
from app.db.models import Company, JobListing, UserProfile  # noqa: F401

# Configure engine based on database type
connect_args = {}
pool_settings = {}

if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread for FastAPI
    connect_args = {"check_same_thread": False}
else:
    # PostgreSQL connection pooling settings
    pool_settings = {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,  # Verify connections before use
    }

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
    connect_args=connect_args,
    **pool_settings
)


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

