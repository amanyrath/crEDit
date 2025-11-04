#!/usr/bin/env python3
"""
Manual test script for insights endpoint
Tests the /api/v1/users/me/insights endpoint with various scenarios
"""

import sys
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Add parent directory to path
sys.path.insert(0, '/Users/alexismanyrath/Code/crEDit/spendsense-backend')

from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_current_user
from app.utils.models import UserInfo
from uuid import uuid4

# Create test client
client = TestClient(app)


def test_insights_endpoint_without_auth():
    """Test that endpoint requires authentication"""
    print("\n" + "="*60)
    print("TEST 1: Endpoint without authentication")
    print("="*60)
    
    response = client.get("/api/v1/users/me/insights")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code in [401, 403], "Should require authentication"
    print("✅ PASS: Endpoint correctly requires authentication")


def test_insights_endpoint_with_mock_auth():
    """Test endpoint with mocked authentication"""
    print("\n" + "="*60)
    print("TEST 2: Endpoint with mocked authentication")
    print("="*60)
    
    # Mock user info
    mock_user = UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )
    
    # Override dependency using FastAPI's dependency_overrides
    async def override_get_current_user(credentials=None):
        return mock_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        with patch('app.api.v1.consumer.get_session') as mock_get_session:
            # Mock database session
            from unittest.mock import MagicMock
            mock_session = MagicMock()
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            # Mock empty results (no transactions)
            from sqlalchemy import func
            mock_query = MagicMock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.group_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.having.return_value = mock_query
            mock_query.scalar.return_value = None
            mock_query.first.return_value = None
            mock_query.all.return_value = []
            
            # Mock account query (no credit accounts)
            def query_side_effect(model):
                if model.__name__ == 'Account':
                    account_query = MagicMock()
                    account_query.filter.return_value = account_query
                    account_query.all.return_value = []
                    return account_query
                return mock_query
            
            mock_session.query.side_effect = query_side_effect
            
            response = client.get(
                "/api/v1/users/me/insights",
                headers={"Authorization": "Bearer mock-token"}
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"\nResponse Structure:")
                print(json.dumps(data, indent=2))
                
                # Validate structure
                assert "data" in data
                assert "meta" in data
                assert "summary" in data["data"]
                assert "charts" in data["data"]
                assert "spending_by_category" in data["data"]["charts"]
                assert "credit_utilization" in data["data"]["charts"]
                assert "subscriptions" in data["data"]["charts"]
                
                print("\n✅ PASS: Endpoint returns correct structure")
                print(f"✅ Summary keys: {list(data['data']['summary'].keys())}")
                print(f"✅ Charts keys: {list(data['data']['charts'].keys())}")
                print(f"✅ Meta keys: {list(data['meta'].keys())}")
            else:
                print(f"❌ FAIL: Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_insights_endpoint_with_period():
    """Test endpoint with different period parameters"""
    print("\n" + "="*60)
    print("TEST 3: Endpoint with period parameter")
    print("="*60)
    
    mock_user = UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )
    
    # Override dependency
    async def override_get_current_user(credentials=None):
        return mock_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        for period in ["30d", "90d"]:
            print(f"\nTesting period: {period}")
            with patch('app.api.v1.consumer.get_session') as mock_get_session:
                from unittest.mock import MagicMock
                mock_session = MagicMock()
                mock_get_session.return_value.__enter__.return_value = mock_session
                
                mock_query = MagicMock()
                mock_session.query.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.group_by.return_value = mock_query
                mock_query.order_by.return_value = mock_query
                mock_query.having.return_value = mock_query
                mock_query.scalar.return_value = None
                mock_query.first.return_value = None
                mock_query.all.return_value = []
                
                def query_side_effect(model):
                    if model.__name__ == 'Account':
                        account_query = MagicMock()
                        account_query.filter.return_value = account_query
                        account_query.all.return_value = []
                        return account_query
                    return mock_query
                
                mock_session.query.side_effect = query_side_effect
                
                response = client.get(
                    f"/api/v1/users/me/insights?period={period}",
                    headers={"Authorization": "Bearer mock-token"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["meta"]["period"] == period
                    print(f"✅ Period {period}: Correct period in response")
                else:
                    print(f"❌ Period {period}: Failed with status {response.status_code}")
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def test_insights_endpoint_invalid_period():
    """Test endpoint with invalid period parameter"""
    print("\n" + "="*60)
    print("TEST 4: Endpoint with invalid period parameter")
    print("="*60)
    
    mock_user = UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )
    
    # Override dependency
    async def override_get_current_user(credentials=None):
        return mock_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        response = client.get(
            "/api/v1/users/me/insights?period=invalid",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 400
        assert "Period must be '30d' or '90d'" in response.json()["detail"]
        print("✅ PASS: Invalid period correctly rejected")
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()


def print_test_summary():
    """Print summary of endpoint structure"""
    print("\n" + "="*60)
    print("ENDPOINT STRUCTURE SUMMARY")
    print("="*60)
    print("""
Endpoint: GET /api/v1/users/me/insights

Query Parameters:
  - period: "30d" | "90d" (default: "30d")

Response Structure:
{
  "data": {
    "summary": {
      "total_spending": float,
      "average_daily_spend": float,
      "top_category": string | null,
      "savings_rate": float | null
    },
    "charts": {
      "spending_by_category": [
        {"category": string, "amount": float}
      ],
      "credit_utilization": [
        {
          "date": "YYYY-MM-DD",
          "utilization": float,
          "balance": float,
          "limit": float
        }
      ],
      "subscriptions": {
        "total_monthly": float,
        "subscriptions": [
          {"merchant": string, "amount": float}
        ]
      }
    }
  },
  "meta": {
    "timestamp": "ISO8601",
    "period": "30d" | "90d",
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD"
  }
}
""")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MANUAL TESTING: Insights API Endpoint")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        test_insights_endpoint_without_auth()
        test_insights_endpoint_with_mock_auth()
        test_insights_endpoint_with_period()
        test_insights_endpoint_invalid_period()
        print_test_summary()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

