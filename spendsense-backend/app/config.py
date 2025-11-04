"""Configuration management"""

import os
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings"""

    # Database
    database_url: Optional[str] = os.getenv("DATABASE_URL")

    # AWS Cognito
    cognito_user_pool_id: Optional[str] = os.getenv("COGNITO_USER_POOL_ID")
    cognito_client_id: Optional[str] = os.getenv("COGNITO_CLIENT_ID")

    # AWS
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")

    # OpenAI / LLM
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()

