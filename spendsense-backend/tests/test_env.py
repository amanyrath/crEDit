"""
Test file to verify environment variables are loaded correctly
This file can be run with: pytest tests/test_env.py
"""

import os
import pytest
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def test_database_url_loaded():
    """Test that DATABASE_URL is loaded from .env file"""
    database_url = os.getenv("DATABASE_URL")
    assert database_url is not None, "DATABASE_URL should be defined in .env file"
    assert database_url.startswith("postgresql://"), "DATABASE_URL should be a PostgreSQL connection string"


def test_cognito_variables_loaded():
    """Test that Cognito environment variables are loaded"""
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    
    assert user_pool_id is not None, "COGNITO_USER_POOL_ID should be defined in .env file"
    assert client_id is not None, "COGNITO_CLIENT_ID should be defined in .env file"


def test_aws_region_loaded():
    """Test that AWS_REGION is loaded (should default to us-east-1)"""
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    assert aws_region == "us-east-1", "AWS_REGION should default to us-east-1"


def test_llm_api_key_loaded():
    """Test that at least one LLM API key is configured"""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    # At least one should be set (though it may be a placeholder)
    assert (
        openai_key is not None or anthropic_key is not None
    ), "At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) should be defined in .env file"


def test_settings_import():
    """Test that settings can be imported and accessed"""
    from app.config import settings
    
    assert settings.database_url is not None, "settings.database_url should be loaded"
    assert settings.cognito_user_pool_id is not None, "settings.cognito_user_pool_id should be loaded"
    assert settings.cognito_client_id is not None, "settings.cognito_client_id should be loaded"
    assert settings.aws_region == "us-east-1", "settings.aws_region should default to us-east-1"

