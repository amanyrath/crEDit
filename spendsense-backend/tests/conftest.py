"""pytest configuration and fixtures"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    """Set test environment variables to prevent AWS credential lookup during tests."""
    # Set a dummy database URL for tests (tests mock the database anyway)
    os.environ['DATABASE_URL'] = os.environ.get(
        'DATABASE_URL',
        'postgresql://test:test@localhost:5432/test'
    )
    # Set required Cognito variables (tests mock these anyway)
    os.environ['COGNITO_USER_POOL_ID'] = os.environ.get(
        'COGNITO_USER_POOL_ID',
        'test-pool-id'
    )
    os.environ['COGNITO_CLIENT_ID'] = os.environ.get(
        'COGNITO_CLIENT_ID',
        'test-client-id'
    )
    # Set LLM API keys (tests mock these anyway)
    os.environ['OPENAI_API_KEY'] = os.environ.get(
        'OPENAI_API_KEY',
        'test-openai-key'
    )
    os.environ['AWS_REGION'] = os.environ.get(
        'AWS_REGION',
        'us-east-1'
    )
    yield
    # Cleanup if needed


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)



