import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import sys
import os
from pathlib import Path

# Add the root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from app.core.dependencies import get_db
from app.config import settings

# -------------------------------------------------------------------------------
# Environment Configuration
# -------------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_env():
    """Provide test environment configuration."""
    # Save original environment
    original_env = os.environ.copy()
    
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["LOG_LEVEL"] = "ERROR"
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)

# -------------------------------------------------------------------------------
# FastAPI Test Client
# -------------------------------------------------------------------------------

@pytest.fixture
def client():
    """
    Test client for making HTTP requests with mocked database.
    """
    # Use a mock database for tests
    mock_db = MagicMock()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield mock_db
        finally:
            pass
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Reset overrides after test
    app.dependency_overrides.clear()

# -------------------------------------------------------------------------------
# Common Test Utilities 
# -------------------------------------------------------------------------------

@pytest.fixture
def sample_wikipedia_url():
    """Provide a sample valid Wikipedia URL."""
    return "https://en.wikipedia.org/wiki/Python_(programming_language)"

@pytest.fixture
def sample_wikipedia_content():
    """Provide sample Wikipedia page content."""
    with open(Path(__file__).parent / "data" / "sample_wikipedia_content.html", "r", encoding="utf-8") as f:
        return f.read()

# -------------------------------------------------------------------------------
# Placeholder for Future Database Integration Tests
# -------------------------------------------------------------------------------

# These fixtures will be implemented when we add integration tests
# They are commented out until needed

"""
@pytest.fixture(scope="session")
def pg_engine():
    \"""Create a PostgreSQL engine for testing.\"""
    # Will be implemented for integration tests
    pass

@pytest.fixture(scope="function")
def pg_test_db():
    \"""Create tables and return a test database session.\"""
    # Will be implemented for integration tests
    pass
"""
