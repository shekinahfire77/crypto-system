"""Test configuration and fixtures."""

import asyncio
import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Settings
from database.models import Base
from database.connection import get_db_session


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_url():
    """Get test database URL."""
    # Use SQLite for testing
    return "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create test database engine."""
    engine = create_engine(test_db_url, echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_settings():
    """Create test settings."""
    return Settings(
        coingecko_api_key="test_coingecko_key",
        cmc_api_key="test_cmc_key",
        cmc_dex_api_key="test_cmc_dex_key",
        coingecko_rate_limit=15,
        cmc_rate_limit=15,
        cmc_dex_rate_limit=50,
        db_host="localhost",
        db_port=5432,
        db_name="test_crypto_market",
        db_user="test_user",
        db_password="test_pass",
    )
