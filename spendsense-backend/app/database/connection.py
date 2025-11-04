"""Database connection management"""

import json
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from sqlalchemy import create_engine, Engine

from app.config import settings


def get_db_url_from_secrets_manager() -> Optional[str]:
    """Retrieve database connection string from AWS Secrets Manager"""
    if not settings.database_url:
        try:
            secrets_client = boto3.client("secretsmanager", region_name=settings.aws_region)
            secret_name = os.getenv("DATABASE_SECRET_NAME", "spendsense/database/connection")
            response = secrets_client.get_secret_value(SecretId=secret_name)
            secret_value = response["SecretString"]
            
            # Try to parse as JSON (connection string secret is stored as JSON)
            try:
                secret_json = json.loads(secret_value)
                # Check if connection_string field exists
                if "connection_string" in secret_json:
                    return secret_json["connection_string"]
                # Otherwise, construct from individual fields
                elif "host" in secret_json and "username" in secret_json and "password" in secret_json:
                    host = secret_json["host"]
                    port = secret_json.get("port", "5432")
                    database = secret_json.get("database", "spendsense")
                    username = secret_json["username"]
                    password = secret_json["password"]
                    return f"postgresql://{username}:{password}@{host}:{port}/{database}"
            except json.JSONDecodeError:
                # If not JSON, assume it's a plain connection string
                return secret_value
                
        except ClientError as e:
            print(f"Error retrieving database secret: {e}")
            return None
    return None


def get_db_url() -> str:
    """
    Get database URL from environment variable or Secrets Manager
    
    Returns:
        Database connection string in format: postgresql://user:pass@host:5432/dbname
    """
    # Try environment variable first (for local development)
    db_url = settings.database_url
    
    # If not in environment, try Secrets Manager (for production)
    if not db_url:
        db_url = get_db_url_from_secrets_manager()
    
    if not db_url:
        raise ValueError(
            "DATABASE_URL not found in environment variables or Secrets Manager. "
            "Please set DATABASE_URL environment variable or configure Secrets Manager."
        )
    
    return db_url


def get_engine(pool_size: int = 5, max_overflow: int = 10) -> Engine:
    """
    Create SQLAlchemy engine with connection pooling
    
    Args:
        pool_size: Number of connections to maintain in the pool
        max_overflow: Maximum number of connections to allow beyond pool_size
        
    Returns:
        SQLAlchemy engine instance
    """
    db_url = get_db_url()
    
    # Ensure SSL is required for RDS connections
    # Add sslmode=require if not already present
    if "sslmode" not in db_url:
        separator = "&" if "?" in db_url else "?"
        db_url = f"{db_url}{separator}sslmode=require"
    
    # Configure connection pool for Lambda functions
    # Use connection pooling to manage RDS connections efficiently
    engine = create_engine(
        db_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=True,  # Verify connections before using them
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.environment == "development",  # Log SQL in development
        connect_args={
            "sslmode": "require"  # Require SSL for RDS connections
        } if "postgresql" in db_url else {},
    )
    
    return engine

