"""Dependency injection for FastAPI - Authentication and Authorization"""

from typing import Annotated
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.jwt import extract_user_info
from app.utils.models import UserInfo


security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> UserInfo:
    """
    FastAPI dependency to extract and validate JWT token
    Returns UserInfo if token is valid
    Raises HTTPException with 401 if token is invalid or missing
    """
    try:
        token = credentials.credentials
        user_info_dict = extract_user_info(token)
        return UserInfo(**user_info_dict)
    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(required_role: str):
    """
    FastAPI dependency factory for role-based access control
    Returns a dependency that checks if user has the required role
    
    Args:
        required_role: "consumer" or "operator"
    
    Returns:
        Dependency function that raises 403 if role doesn't match
    """
    async def role_checker(
        current_user: Annotated[UserInfo, Depends(get_current_user)]
    ) -> UserInfo:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return current_user
    
    return role_checker


async def require_operator(
    current_user: Annotated[UserInfo, Depends(get_current_user)]
) -> UserInfo:
    """
    FastAPI dependency for operator-only endpoints
    Raises 403 if user is not an operator
    """
    if current_user.role != "operator":
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions. Operator role required.",
        )
    return current_user


async def require_consumer(
    current_user: Annotated[UserInfo, Depends(get_current_user)]
) -> UserInfo:
    """
    FastAPI dependency for consumer endpoints
    Allows any authenticated user (consumer or operator can access consumer endpoints)
    """
    # Consumer endpoints allow all authenticated users
    return current_user
