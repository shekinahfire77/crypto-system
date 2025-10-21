"""Database connection management."""

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import get_settings


@lru_cache(maxsize=1)
def get_db_engine() -> Engine:
    """Create and return database engine (cached as singleton).

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
    """Get a database session using cached engine.

    Returns:
        SQLAlchemy Session instance
    """
    engine = get_db_engine()  # Returns cached singleton
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    return SessionLocal()
