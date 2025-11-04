"""Operator API endpoints - accessible only to operators"""

from fastapi import APIRouter, Depends
from app.dependencies import require_operator, UserInfo

router = APIRouter(prefix="/operator", tags=["operator"])


@router.get("/users")
async def list_users(
    current_user: UserInfo = Depends(require_operator),
):
    """List all users (operator only)"""
    return {
        "users": [],
        "message": "User list endpoint - to be implemented",
    }


@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: UserInfo = Depends(require_operator),
):
    """Get operator dashboard statistics"""
    return {
        "message": "Operator dashboard endpoint",
        "operator_id": current_user.user_id,
    }

