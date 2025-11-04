"""pytest configuration and fixtures"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope='session', autouse=True)
def set_test_database_url():
    """Set a test DATABASE_URL to prevent AWS credential lookup during tests."""
    # Set a dummy database URL for tests (tests mock the database anyway)
    os.environ['DATABASE_URL'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://test:test@localhost:5432/test'
    )
    yield
    # Cleanup if needed


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)



