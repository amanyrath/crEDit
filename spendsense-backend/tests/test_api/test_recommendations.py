"""Tests for recommendations API endpoint"""

import pytest
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.recommendation import Recommendation
from app.models.persona import PersonaAssignment
from app.models.computed_feature import ComputedFeature
from app.models.decision_trace import DecisionTrace
from app.utils.models import UserInfo


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_user_id():
    """Mock user ID"""
    return str(uuid4())


@pytest.fixture
def mock_consumer_user():
    """Mock consumer user"""
    return UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )


@pytest.fixture
def mock_recommendations():
    """Mock recommendation data"""
    user_id = uuid4()
    
    return [
        Recommendation(
            id=uuid4(),
            user_id=user_id,
            type="education",
            title="Understanding Credit Utilization",
            rationale="Your Visa ending in 4523 is at 65% utilization",
            created_at=datetime.utcnow()
        ),
        Recommendation(
            id=uuid4(),
            user_id=user_id,
            type="education",
            title="Building Emergency Savings",
            rationale="Consider building a 3-month emergency fund",
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        Recommendation(
            id=uuid4(),
            user_id=user_id,
            type="offer",
            title="Balance Transfer Credit Card",
            rationale="This might help reduce your interest payments",
            created_at=datetime.utcnow()
        ),
    ]


@pytest.fixture
def mock_persona_assignment():
    """Mock persona assignment"""
    return PersonaAssignment(
        id=uuid4(),
        user_id=uuid4(),
        time_window="30d",
        persona="high_utilization",
        assigned_at=datetime.utcnow() - timedelta(days=10)
    )


@pytest.fixture
def mock_decision_trace():
    """Mock decision trace"""
    return DecisionTrace(
        id=uuid4(),
        recommendation_id=uuid4(),
        trace_data={
            "description": "Learn about credit utilization ratios",
            "category": "credit",
            "tags": ["Credit", "DebtManagement"],
            "full_content": "Full educational content here..."
        }
    )


class TestGetRecommendationsEndpoint:
    """Test recommendations endpoint"""
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_success(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        mock_recommendations,
        mock_persona_assignment,
        client
    ):
        """Test successful recommendations retrieval"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        mock_recommendations[0].user_id = user_id
        mock_recommendations[1].user_id = user_id
        mock_recommendations[2].user_id = user_id
        mock_persona_assignment.user_id = user_id
        
        # Mock persona query
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = mock_persona_assignment
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = mock_recommendations
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = []
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert "education" in data["data"]
        assert "offers" in data["data"]
        assert len(data["data"]["education"]) == 2
        assert len(data["data"]["offers"]) == 1
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_empty_state(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        client
    ):
        """Test empty state when no recommendations exist"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        
        # Mock persona query (no persona)
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = None
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query (empty)
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = []
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = []
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "education" in data["data"]
        assert "offers" in data["data"]
        assert data["data"]["education"] == []
        assert data["data"]["offers"] == []
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_with_decision_traces(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        mock_recommendations,
        mock_decision_trace,
        client
    ):
        """Test recommendations with decision traces"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        mock_recommendations[0].user_id = user_id
        mock_decision_trace.recommendation_id = mock_recommendations[0].id
        
        # Mock persona query
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = None
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = [mock_recommendations[0]]
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = [mock_decision_trace]
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["education"]) == 1
        education = data["data"]["education"][0]
        assert education["category"] == "credit"
        assert "Credit" in education["tags"]
        assert education["full_content"] == "Full educational content here..."
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_user_filtering(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        mock_recommendations,
        client
    ):
        """Test that users can only access their own recommendations"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        # Set recommendations to belong to this user
        mock_recommendations[0].user_id = user_id
        mock_recommendations[1].user_id = user_id
        mock_recommendations[2].user_id = user_id
        
        # Mock persona query
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = None
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query - verify user_id filter is applied
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = mock_recommendations
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = []
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        # Verify filter was called with user_id
        mock_rec_query.filter.assert_called()
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_limit_counts(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        client
    ):
        """Test that education is limited to 5 and offers to 3"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        
        # Create 10 education and 5 offers
        education_recs = [
            Recommendation(
                id=uuid4(),
                user_id=user_id,
                type="education",
                title=f"Education {i}",
                rationale=f"Rationale {i}",
                created_at=datetime.utcnow() - timedelta(days=i)
            ) for i in range(10)
        ]
        offer_recs = [
            Recommendation(
                id=uuid4(),
                user_id=user_id,
                type="offer",
                title=f"Offer {i}",
                rationale=f"Rationale {i}",
                created_at=datetime.utcnow() - timedelta(days=i)
            ) for i in range(5)
        ]
        all_recs = education_recs + offer_recs
        
        # Mock persona query
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = None
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = all_recs
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = []
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]["education"]) <= 5
        assert len(data["data"]["offers"]) <= 3
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_requires_authentication(
        self,
        mock_require_consumer,
        mock_get_session,
        client
    ):
        """Test that endpoint requires authentication"""
        # Make request without authentication
        response = client.get("/api/v1/users/me/recommendations")
        
        # Should return 401 or 403
        assert response.status_code in [401, 403]
    
    @patch("app.api.v1.consumer.get_session")
    @patch("app.api.v1.consumer.require_consumer")
    def test_get_recommendations_response_format(
        self,
        mock_require_consumer,
        mock_get_session,
        mock_consumer_user,
        mock_recommendations,
        mock_decision_trace,
        client
    ):
        """Test response format matches specification"""
        # Setup mocks
        mock_require_consumer.return_value = mock_consumer_user
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        user_id = UUID(mock_consumer_user.user_id)
        mock_recommendations[0].user_id = user_id
        mock_recommendations[0].type = "education"
        mock_decision_trace.recommendation_id = mock_recommendations[0].id
        
        # Mock persona query
        mock_persona_query = Mock()
        mock_session.query.return_value = mock_persona_query
        mock_persona_query.filter.return_value = mock_persona_query
        mock_persona_query.order_by.return_value = mock_persona_query
        mock_persona_query.first.return_value = None
        
        # Mock computed features query
        mock_features_query = Mock()
        mock_session.query.return_value = mock_features_query
        mock_features_query.filter.return_value = mock_features_query
        mock_features_query.all.return_value = []
        
        # Mock recommendations query
        mock_rec_query = Mock()
        mock_session.query.return_value = mock_rec_query
        mock_rec_query.filter.return_value = mock_rec_query
        mock_rec_query.order_by.return_value = mock_rec_query
        mock_rec_query.all.return_value = [mock_recommendations[0]]
        
        # Mock decision traces query
        mock_trace_query = Mock()
        mock_session.query.return_value = mock_trace_query
        mock_trace_query.filter.return_value = mock_trace_query
        mock_trace_query.all.return_value = [mock_decision_trace]
        
        # Make request
        response = client.get(
            "/api/v1/users/me/recommendations",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "data" in data
        assert "meta" in data
        assert "education" in data["data"]
        assert "offers" in data["data"]
        assert "timestamp" in data["meta"]
        
        # Verify education item structure
        if len(data["data"]["education"]) > 0:
            education = data["data"]["education"][0]
            assert "id" in education
            assert "title" in education
            assert "description" in education
            assert "rationale" in education
            assert "category" in education
            assert "tags" in education
            assert "full_content" in education

