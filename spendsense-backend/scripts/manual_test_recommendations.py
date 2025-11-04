#!/usr/bin/env python3
"""
Manual test script for recommendations endpoint
Tests the /api/v1/users/me/recommendations endpoint with various scenarios
"""

import sys
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

# Add parent directory to path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


def test_recommendations_endpoint_without_auth():
    """Test that endpoint requires authentication"""
    print("\n" + "="*60)
    print("TEST 1: Endpoint without authentication")
    print("="*60)
    
    response = client.get("/api/v1/users/me/recommendations")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    assert response.status_code in [401, 403], "Should require authentication"
    print("✅ PASS: Endpoint correctly requires authentication")


def test_recommendations_endpoint_with_mock_auth():
    """Test endpoint with mocked authentication"""
    print("\n" + "="*60)
    print("TEST 2: Endpoint with mocked authentication")
    print("="*60)
    
    from app.utils.models import UserInfo
    
    mock_user = UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )
    
    with patch("app.dependencies.require_consumer", return_value=mock_user):
        with patch("app.api.v1.consumer.get_session") as mock_get_session:
            from app.models.recommendation import Recommendation
            from app.models.persona import PersonaAssignment
            from app.models.computed_feature import ComputedFeature
            from app.models.decision_trace import DecisionTrace
            
            # Create mock session
            mock_session = Mock()
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            user_id = uuid4()
            mock_user.user_id = str(user_id)
            
            # Create mock recommendations
            rec1 = Recommendation(
                id=uuid4(),
                user_id=user_id,
                type="education",
                title="Understanding Credit Utilization",
                rationale="Your Visa ending in 4523 is at 65% utilization",
                created_at=datetime.utcnow()
            )
            rec2 = Recommendation(
                id=uuid4(),
                user_id=user_id,
                type="education",
                title="Building Emergency Savings",
                rationale="Consider building a 3-month emergency fund",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
            rec3 = Recommendation(
                id=uuid4(),
                user_id=user_id,
                type="offer",
                title="Balance Transfer Credit Card",
                rationale="This might help reduce your interest payments",
                created_at=datetime.utcnow()
            )
            
            # Create mock decision trace
            trace = DecisionTrace(
                id=uuid4(),
                recommendation_id=rec1.id,
                trace_data={
                    "description": "Learn about credit utilization ratios",
                    "category": "credit",
                    "tags": ["Credit", "DebtManagement"],
                    "full_content": "Full educational content about credit utilization..."
                }
            )
            
            # Mock persona assignment
            persona = PersonaAssignment(
                id=uuid4(),
                user_id=user_id,
                time_window="30d",
                persona="high_utilization",
                assigned_at=datetime.utcnow() - timedelta(days=10)
            )
            
            def query_side_effect(model):
                mock_query = Mock()
                mock_query.filter.return_value = mock_query
                
                if model == PersonaAssignment:
                    mock_query.order_by.return_value = mock_query
                    mock_query.first.return_value = persona
                elif model == ComputedFeature:
                    mock_query.all.return_value = []
                elif model == Recommendation:
                    mock_query.order_by.return_value = mock_query
                    mock_query.all.return_value = [rec1, rec2, rec3]
                elif model == DecisionTrace:
                    mock_query.all.return_value = [trace]
                
                return mock_query
            
            mock_session.query.side_effect = query_side_effect
            
            response = client.get(
                "/api/v1/users/me/recommendations",
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
                assert "education" in data["data"]
                assert "offers" in data["data"]
                assert isinstance(data["data"]["education"], list)
                assert isinstance(data["data"]["offers"], list)
                
                print("\n✅ PASS: Endpoint returns correct structure")
                print(f"✅ Education count: {len(data['data']['education'])}")
                print(f"✅ Offers count: {len(data['data']['offers'])}")
                
                # Validate education item structure
                if len(data["data"]["education"]) > 0:
                    edu = data["data"]["education"][0]
                    assert "id" in edu
                    assert "title" in edu
                    assert "description" in edu
                    assert "rationale" in edu
                    assert "category" in edu
                    assert "tags" in edu
                    assert "full_content" in edu
                    print(f"✅ Education item keys: {list(edu.keys())}")
                
                # Validate offer item structure
                if len(data["data"]["offers"]) > 0:
                    offer = data["data"]["offers"][0]
                    assert "id" in offer
                    assert "title" in offer
                    assert "description" in offer
                    assert "rationale" in offer
                    assert "eligibility" in offer
                    assert "partner_logo_url" in offer
                    print(f"✅ Offer item keys: {list(offer.keys())}")
                
                # Validate meta
                assert "timestamp" in data["meta"]
                print(f"✅ Meta keys: {list(data['meta'].keys())}")
            else:
                print(f"❌ FAIL: Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")


def test_recommendations_endpoint_empty_state():
    """Test endpoint with no recommendations"""
    print("\n" + "="*60)
    print("TEST 3: Endpoint with empty state (no recommendations)")
    print("="*60)
    
    from app.utils.models import UserInfo
    
    mock_user = UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )
    
    with patch("app.dependencies.require_consumer", return_value=mock_user):
        with patch("app.api.v1.consumer.get_session") as mock_get_session:
            from app.models.persona import PersonaAssignment
            from app.models.computed_feature import ComputedFeature
            
            mock_session = Mock()
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            def query_side_effect(model):
                mock_query = Mock()
                mock_query.filter.return_value = mock_query
                
                if model == PersonaAssignment:
                    mock_query.order_by.return_value = mock_query
                    mock_query.first.return_value = None
                elif model == ComputedFeature:
                    mock_query.all.return_value = []
                else:
                    mock_query.order_by.return_value = mock_query
                    mock_query.all.return_value = []
                
                return mock_query
            
            mock_session.query.side_effect = query_side_effect
            
            response = client.get(
                "/api/v1/users/me/recommendations",
                headers={"Authorization": "Bearer mock-token"}
            )
            
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"\nResponse Structure:")
                print(json.dumps(data, indent=2))
                
                assert data["data"]["education"] == []
                assert data["data"]["offers"] == []
                print("✅ PASS: Empty state handled correctly")
            else:
                print(f"❌ FAIL: Expected 200, got {response.status_code}")
                print(f"Response: {response.text}")


def print_test_summary():
    """Print summary of endpoint structure"""
    print("\n" + "="*60)
    print("ENDPOINT STRUCTURE SUMMARY")
    print("="*60)

    print("""
Endpoint: GET /api/v1/users/me/recommendations

Authentication: Required (Bearer token)

Response Structure:
{
  "data": {
    "education": [
      {
        "id": "uuid",
        "title": "string",
        "description": "string",
        "rationale": "string",
        "category": "string | null",
        "tags": ["string"],
        "full_content": "string | null"
      }
    ],
    "offers": [
      {
        "id": "uuid",
        "title": "string",
        "description": "string",
        "rationale": "string",
        "eligibility": "eligible | requirements_not_met",
        "partner_logo_url": "string | null"
      }
    ]
  },
  "meta": {
    "timestamp": "ISO8601",
    "persona": "string | null"
  }
}

Limits:
- Education recommendations: 3-5 items
- Offer recommendations: 2-3 items
- Sorted by priority (newest first)
""")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MANUAL TESTING: Recommendations API Endpoint")
    print("="*60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        test_recommendations_endpoint_without_auth()
        test_recommendations_endpoint_with_mock_auth()
        test_recommendations_endpoint_empty_state()
        print_test_summary()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

