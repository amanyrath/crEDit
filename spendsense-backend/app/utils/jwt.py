"""JWT token validation utilities for AWS Cognito"""

import json
import time
from typing import Dict, Optional, Any
from functools import lru_cache

import requests
from jose import jwt, JWTError
from jose.constants import ALGORITHMS

from app.config import settings


# Cache for JWKS keys (cached for 1 hour)
_jwks_cache: Optional[Dict[str, Any]] = None
_jwks_cache_time: float = 0
JWKS_CACHE_TTL = 3600  # 1 hour


def get_jwks_url() -> str:
    """Construct Cognito JWKS URL from user pool ID and region"""
    if not settings.cognito_user_pool_id:
        raise ValueError("COGNITO_USER_POOL_ID not configured")
    
    region = settings.aws_region
    user_pool_id = settings.cognito_user_pool_id
    
    return f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"


def fetch_jwks() -> Dict[str, Any]:
    """Fetch JWKS keys from Cognito"""
    global _jwks_cache, _jwks_cache_time
    
    # Check cache
    current_time = time.time()
    if _jwks_cache is not None and (current_time - _jwks_cache_time) < JWKS_CACHE_TTL:
        return _jwks_cache
    
    # Fetch from Cognito
    jwks_url = get_jwks_url()
    response = requests.get(jwks_url, timeout=10)
    response.raise_for_status()
    
    jwks = response.json()
    
    # Update cache
    _jwks_cache = jwks
    _jwks_cache_time = current_time
    
    return jwks


def get_signing_key(token: str, jwks: Dict[str, Any]) -> Any:
    """Get the signing key from JWKS based on token header"""
    try:
        # Decode token header without verification
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        if not kid:
            raise ValueError("Token header missing 'kid'")
        
        # Find matching key in JWKS
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return key
        
        raise ValueError(f"Key with kid '{kid}' not found in JWKS")
    except JWTError as e:
        raise ValueError(f"Invalid token header: {e}")


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token signature and expiration
    Returns decoded token claims if valid
    Raises ValueError if token is invalid
    """
    if not settings.cognito_user_pool_id:
        raise ValueError("COGNITO_USER_POOL_ID not configured")
    
    # Fetch JWKS
    jwks = fetch_jwks()
    
    # Get signing key
    key = get_signing_key(token, jwks)
    
    # Construct public key from JWK
    public_key = jwt.construct_key(key, ALGORITHMS.RS256)
    
    # Verify token
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=[ALGORITHMS.RS256],
            audience=settings.cognito_client_id,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
            },
        )
        return claims
    except JWTError as e:
        raise ValueError(f"Token validation failed: {e}")


def extract_role_from_claims(claims: Dict[str, Any]) -> str:
    """
    Extract user role from JWT token claims
    
    Priority:
    1. cognito:groups claim (if "operators" group present → "operator")
    2. cognito:groups claim (if "consumers" group present → "consumer")
    3. custom:role claim
    4. Default to "consumer"
    
    Returns: "consumer" or "operator"
    """
    # Check cognito:groups claim (primary method)
    groups = claims.get("cognito:groups", [])
    if isinstance(groups, list):
        if "operators" in groups:
            return "operator"
        if "consumers" in groups:
            return "consumer"
    
    # Fallback to custom:role claim
    custom_role = claims.get("custom:role")
    if custom_role:
        if custom_role in ["consumer", "operator"]:
            return custom_role
    
    # Default to consumer
    return "consumer"


def extract_user_info(token: str) -> Dict[str, Any]:
    """
    Extract user information from JWT token
    
    Returns dict with:
    - user_id: User ID from 'sub' claim
    - role: User role extracted from claims
    - email: User email (if available)
    """
    claims = verify_token(token)
    
    user_id = claims.get("sub")
    if not user_id:
        raise ValueError("Token missing 'sub' claim")
    
    role = extract_role_from_claims(claims)
    email = claims.get("email")
    
    return {
        "user_id": user_id,
        "role": role,
        "email": email,
    }

