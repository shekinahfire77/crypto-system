"""Database connection management."""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings


def get_db_engine() -> Engine:
    """Create and return database engine.

    Returns:
        SQLAlchemy Engine instance
    """
    settings = get_settings()

    engine = create_engine(
        settings.database_url,
        echo=False,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,  # Test connections before using
    )

    return engine


def get_db_session() -> Session:
    """Get a database session.

    Returns:
        SQLAlchemy Session instance
    """
    engine = get_db_engine()
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()
