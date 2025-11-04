"""Consumer API endpoints - accessible to all authenticated users"""

from datetime import date, datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.dependencies import require_consumer, UserInfo
from app.database.session import get_session
from app.models.transaction import Transaction
from app.models.account import Account

router = APIRouter(prefix="/users/me", tags=["consumer"])


# Pydantic models for transactions API
class TransactionQueryParams(BaseModel):
    """Query parameters for transactions endpoint"""
    
    start_date: Optional[date] = Field(None, description="Start date (ISO 8601)")
    end_date: Optional[date] = Field(None, description="End date (ISO 8601)")
    category: Optional[str] = Field(None, description="Filter by category")
    merchant: Optional[str] = Field(None, description="Search merchant name (case-insensitive partial match)")
    page: int = Field(1, ge=1, description="Page number (1-based)")
    limit: int = Field(50, ge=1, le=100, description="Items per page (max 100)")


class TransactionResponse(BaseModel):
    """Transaction response model"""
    
    id: UUID
    user_id: UUID
    account_id: UUID
    date: date
    merchant: str
    amount: float
    category: Optional[str] = None
    
    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    
    page: int
    limit: int
    total: int
    total_pages: int


class TransactionsResponse(BaseModel):
    """Response model for transactions endpoint"""
    
    data: dict = Field(..., description="Response data")
    meta: dict = Field(..., description="Response metadata")


@router.get("/profile")
async def get_profile(
    current_user: UserInfo = Depends(require_consumer),
):
    """Get current user's profile"""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
    }


def get_user_transactions(
    session: Session,
    user_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    merchant: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
) -> tuple[list[Transaction], int]:
    """
    Query transactions for a user with filters and pagination
    
    Args:
        session: Database session
        user_id: User ID to filter transactions
        start_date: Optional start date filter
        end_date: Optional end date filter
        category: Optional category filter
        merchant: Optional merchant search (case-insensitive partial match)
        page: Page number (1-based)
        limit: Items per page
        
    Returns:
        Tuple of (transaction list, total count)
    """
    # Base query filtered by user_id
    query = session.query(Transaction).filter(Transaction.user_id == user_id)
    
    # Apply date filters
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Apply category filter
    if category:
        query = query.filter(Transaction.category == category)
    
    # Apply merchant search (case-insensitive partial match)
    if merchant:
        query = query.filter(Transaction.merchant.ilike(f"%{merchant}%"))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply sorting (date descending, newest first)
    query = query.order_by(desc(Transaction.date))
    
    # Apply pagination
    offset = (page - 1) * limit
    transactions = query.offset(offset).limit(limit).all()
    
    return transactions, total


@router.get("/transactions")
async def get_transactions(
    start_date: Optional[date] = Query(None, description="Start date (ISO 8601)"),
    end_date: Optional[date] = Query(None, description="End date (ISO 8601)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    merchant: Optional[str] = Query(None, description="Search merchant name"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    limit: int = Query(50, ge=1, le=100, description="Items per page (max 100)"),
    current_user: UserInfo = Depends(require_consumer),
) -> dict:
    """
    Get current user's transactions with filters and pagination
    
    Query Parameters:
    - start_date: Optional start date filter (ISO 8601)
    - end_date: Optional end date filter (ISO 8601)
    - category: Optional category filter
    - merchant: Optional merchant search (case-insensitive partial match)
    - page: Page number (default: 1)
    - limit: Items per page (default: 50, max: 100)
    
    Returns:
        Transactions response with data and pagination metadata
    """
    try:
        # Convert user_id string to UUID
        user_id = UUID(current_user.user_id)
        
        # Query transactions
        with get_session() as session:
            transactions, total = get_user_transactions(
                session=session,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                category=category,
                merchant=merchant,
                page=page,
                limit=limit,
            )
            
            # Calculate total pages
            total_pages = (total + limit - 1) // limit if total > 0 else 0
            
            # Serialize transactions
            transaction_data = [
                {
                    "id": str(t.id),
                    "user_id": str(t.user_id),
                    "account_id": str(t.account_id),
                    "date": t.date.isoformat(),
                    "merchant": t.merchant,
                    "amount": float(t.amount),
                    "category": t.category,
                }
                for t in transactions
            ]
            
            # Build response
            return {
                "data": {
                    "transactions": transaction_data,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "total_pages": total_pages,
                    },
                },
                "meta": {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/insights")
async def get_insights(
    period: str = Query("30d", description="Time period: '30d' or '90d'"),
    current_user: UserInfo = Depends(require_consumer),
) -> dict:
    """
    Get current user's spending insights and charts data
    
    Query Parameters:
    - period: Time period for insights ("30d" or "90d", default: "30d")
    
    Returns:
        Insights response with summary cards and chart data
    """
    from datetime import datetime as dt
    
    # Validate period parameter
    if period not in ["30d", "90d"]:
        raise HTTPException(status_code=400, detail="Period must be '30d' or '90d'")
    
    try:
        user_id = UUID(current_user.user_id)
        
        # Calculate date range
        end_date = date.today()
        if period == "30d":
            start_date = end_date - timedelta(days=30)
        else:  # 90d
            start_date = end_date - timedelta(days=90)
        
        days_in_period = (end_date - start_date).days
        
        with get_session() as session:
            # Task 2: Compute summary cards data
            # Total spending (sum of debit amounts - negative amounts)
            total_spending_result = session.query(
                func.sum(func.abs(Transaction.amount)).label("total")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0  # Only debits (negative amounts)
            ).scalar()
            
            total_spending = float(total_spending_result) if total_spending_result else 0.0
            average_daily_spend = total_spending / days_in_period if days_in_period > 0 else 0.0
            
            # Top category (category with highest total spending)
            top_category_result = session.query(
                Transaction.category,
                func.sum(func.abs(Transaction.amount)).label("category_total")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0,
                Transaction.category.isnot(None)
            ).group_by(
                Transaction.category
            ).order_by(
                desc(func.sum(func.abs(Transaction.amount)))
            ).first()
            
            top_category = top_category_result[0] if top_category_result else None
            
            # Savings rate (savings deposits / total income)
            # For MVP, we'll set this to None if not easily calculable
            # This can be enhanced later with income detection logic
            savings_rate = None
            
            # Task 3: Compute spending by category chart data
            category_spending = session.query(
                Transaction.category,
                func.sum(func.abs(Transaction.amount)).label("amount")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0,
                Transaction.category.isnot(None)
            ).group_by(
                Transaction.category
            ).order_by(
                desc("amount")
            ).all()
            
            spending_by_category = [
                {"category": row[0], "amount": float(row[1])}
                for row in category_spending
            ]
            
            # Task 4: Compute credit utilization trend
            # Check if user has credit card accounts
            credit_accounts = session.query(Account).filter(
                Account.user_id == user_id,
                Account.account_type == "credit_card"
            ).all()
            
            credit_utilization = []
            if credit_accounts:
                # Group by week buckets
                # For simplicity, we'll create weekly buckets
                current_date = start_date
                week_buckets = []
                
                while current_date <= end_date:
                    week_end = min(current_date + timedelta(days=6), end_date)
                    week_buckets.append((current_date, week_end))
                    current_date = week_end + timedelta(days=1)
                
                for week_start, week_end in week_buckets:
                    # Get account balances at end of week (latest transaction date <= week_end)
                    # For MVP, we'll use current account balance as approximation
                    # In production, this would track historical balances
                    for account in credit_accounts:
                        if account.limit and account.limit > 0:
                            balance = abs(float(account.balance)) if account.balance else 0.0
                            limit = float(account.limit)
                            utilization_pct = (balance / limit * 100) if limit > 0 else 0.0
                            
                            credit_utilization.append({
                                "date": week_end.isoformat(),
                                "utilization": round(utilization_pct, 1),
                                "balance": balance,
                                "limit": limit,
                            })
            
            # Task 5: Compute subscription breakdown
            # Identify recurring merchants (simple pattern: same merchant with consistent amounts)
            # For MVP, we'll look for merchants that appear 3+ times with similar amounts
            subscription_merchants = session.query(
                Transaction.merchant,
                func.avg(func.abs(Transaction.amount)).label("avg_amount"),
                func.count(Transaction.id).label("count")
            ).filter(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0
            ).group_by(
                Transaction.merchant
            ).having(
                func.count(Transaction.id) >= 3
            ).all()
            
            subscriptions = []
            total_monthly_recurring = 0.0
            
            for merchant, avg_amount, count in subscription_merchants:
                # Check if amounts are consistent (within 10% variance)
                merchant_transactions = session.query(Transaction.amount).filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                    Transaction.merchant == merchant,
                    Transaction.amount < 0
                ).all()
                
                amounts = [abs(float(t[0])) for t in merchant_transactions]
                if len(amounts) >= 3:
                    avg = sum(amounts) / len(amounts)
                    # Check consistency (within 10% of average)
                    is_consistent = all(
                        abs(amount - avg) / avg <= 0.1 if avg > 0 else False
                        for amount in amounts
                    )
                    
                    if is_consistent:
                        monthly_amount = avg
                        subscriptions.append({
                            "merchant": merchant,
                            "amount": round(monthly_amount, 2)
                        })
                        total_monthly_recurring += monthly_amount
            
            subscription_breakdown = {
                "total_monthly": round(total_monthly_recurring, 2),
                "subscriptions": subscriptions
            }
            
            # Build response
            return {
                "data": {
                    "summary": {
                        "total_spending": round(total_spending, 2),
                        "average_daily_spend": round(average_daily_spend, 2),
                        "top_category": top_category,
                        "savings_rate": savings_rate
                    },
                    "charts": {
                        "spending_by_category": spending_by_category,
                        "credit_utilization": credit_utilization,
                        "subscriptions": subscription_breakdown
                    }
                },
                "meta": {
                    "timestamp": dt.utcnow().isoformat() + "Z",
                    "period": period,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            }
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

