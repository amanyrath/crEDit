"""Pydantic models for user information"""

from pydantic import BaseModel, Field
from typing import Optional


class UserInfo(BaseModel):
    """User information extracted from JWT token"""
    
    user_id: str = Field(..., description="User ID from Cognito (sub claim)")
    role: str = Field(..., description="User role: 'consumer' or 'operator'")
    email: Optional[str] = Field(None, description="User email address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "role": "consumer",
                "email": "user@example.com",
            }
        }

