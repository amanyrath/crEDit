"""Tests for insights API endpoint"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.transaction import Transaction
from app.models.account import Account
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
def mock_transactions():
    """Mock transaction data for insights"""
    user_id = uuid4()
    account_id = uuid4()
    today = date.today()
    
    return [
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=today - timedelta(days=5),
            merchant="Netflix",
            amount=Decimal("-15.99"),
            category="Subscriptions",
        ),
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=today - timedelta(days=10),
            merchant="Netflix",
            amount=Decimal("-15.99"),
            category="Subscriptions",
        ),
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=today - timedelta(days=15),
            merchant="Netflix",
            amount=Decimal("-15.99"),
            category="Subscriptions",
        ),
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=today - timedelta(days=2),
            merchant="Test Restaurant",
            amount=Decimal("-45.50"),
            category="Food & Drink",
        ),
        Transaction(
            id=uuid4(),
            user_id=user_id,
            account_id=account_id,
            date=today - timedelta(days=8),
            merchant="Test Store",
            amount=Decimal("-120.00"),
            category="Shopping",
        ),
    ]


@pytest.fixture
def mock_credit_account():
    """Mock credit card account"""
    user_id = uuid4()
    return Account(
        id=uuid4(),
        user_id=user_id,
        account_type="credit_card",
        balance=Decimal("-3400.00"),
        limit=Decimal("5000.00"),
        account_number_last4="4523"
    )


@pytest.fixture
def mock_consumer_user():
    """Mock consumer user"""
    return UserInfo(
        user_id=str(uuid4()),
        role="consumer",
        email="test@example.com"
    )


class TestInsightsEndpoint:
    """Test insights API endpoint"""
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_without_auth(self, mock_require_consumer, mock_get_session, client):
        """Test endpoint without authentication returns 401"""
        mock_require_consumer.side_effect = Exception("Unauthorized")
        
        response = client.get("/api/v1/users/me/insights")
        assert response.status_code == 401
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_default_period(self, mock_require_consumer, mock_get_session, client, mock_consumer_user, mock_transactions):
        """Test endpoint with default period (30d)"""
        mock_require_consumer.return_value = mock_consumer_user
        
        # Mock database session
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock queries
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = Decimal("195.48")  # Total spending
        mock_query.first.return_value = ("Food & Drink", Decimal("45.50"))  # Top category
        mock_query.all.return_value = [
            ("Food & Drink", Decimal("45.50")),
            ("Shopping", Decimal("120.00")),
            ("Subscriptions", Decimal("47.97"))
        ]
        
        # Mock account query (no credit accounts)
        mock_account_query = Mock()
        mock_session.query.return_value = mock_account_query
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = []
        
        response = client.get(
            "/api/v1/users/me/insights",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert "summary" in data["data"]
        assert "charts" in data["data"]
        assert data["meta"]["period"] == "30d"
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_90d_period(self, mock_require_consumer, mock_get_session, client, mock_consumer_user, mock_transactions):
        """Test endpoint with 90d period"""
        mock_require_consumer.return_value = mock_consumer_user
        
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = Decimal("195.48")
        mock_query.first.return_value = ("Food & Drink", Decimal("45.50"))
        mock_query.all.return_value = [
            ("Food & Drink", Decimal("45.50")),
            ("Shopping", Decimal("120.00")),
            ("Subscriptions", Decimal("47.97"))
        ]
        
        mock_account_query = Mock()
        mock_session.query.return_value = mock_account_query
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = []
        
        response = client.get(
            "/api/v1/users/me/insights",
            params={"period": "90d"},
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["period"] == "90d"
    
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_invalid_period(self, mock_require_consumer, client, mock_consumer_user):
        """Test endpoint with invalid period parameter"""
        mock_require_consumer.return_value = mock_consumer_user
        
        response = client.get(
            "/api/v1/users/me/insights",
            params={"period": "invalid"},
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 400
        assert "Period must be '30d' or '90d'" in response.json()["detail"]
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_with_credit_accounts(self, mock_require_consumer, mock_get_session, client, mock_consumer_user, mock_transactions, mock_credit_account):
        """Test endpoint with credit card accounts"""
        mock_require_consumer.return_value = mock_consumer_user
        
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock transaction queries
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = Decimal("195.48")
        mock_query.first.return_value = ("Food & Drink", Decimal("45.50"))
        mock_query.all.return_value = [
            ("Food & Drink", Decimal("45.50")),
            ("Shopping", Decimal("120.00")),
            ("Subscriptions", Decimal("47.97"))
        ]
        
        # Mock account query to return credit account
        mock_account_query = Mock()
        # Set up query chain to return credit account
        def query_side_effect(model):
            if model == Account:
                return mock_account_query
            return mock_query
        
        mock_session.query.side_effect = query_side_effect
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = [mock_credit_account]
        
        response = client.get(
            "/api/v1/users/me/insights",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "credit_utilization" in data["data"]["charts"]
        # Credit utilization should have data points
        assert len(data["data"]["charts"]["credit_utilization"]) > 0
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_empty_transactions(self, mock_require_consumer, mock_get_session, client, mock_consumer_user):
        """Test endpoint with no transactions"""
        mock_require_consumer.return_value = mock_consumer_user
        
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = None  # No spending
        mock_query.first.return_value = None  # No top category
        mock_query.all.return_value = []  # No category spending
        
        mock_account_query = Mock()
        mock_session.query.side_effect = lambda model: mock_account_query if model == Account else mock_query
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = []
        
        response = client.get(
            "/api/v1/users/me/insights",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["summary"]["total_spending"] == 0.0
        assert data["data"]["summary"]["average_daily_spend"] == 0.0
        assert data["data"]["summary"]["top_category"] is None
        assert data["data"]["charts"]["spending_by_category"] == []
        assert data["data"]["charts"]["credit_utilization"] == []
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_response_structure(self, mock_require_consumer, mock_get_session, client, mock_consumer_user, mock_transactions):
        """Test response structure matches specification"""
        mock_require_consumer.return_value = mock_consumer_user
        
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = Decimal("195.48")
        mock_query.first.return_value = ("Food & Drink", Decimal("45.50"))
        mock_query.all.return_value = [
            ("Food & Drink", Decimal("45.50")),
            ("Shopping", Decimal("120.00")),
            ("Subscriptions", Decimal("47.97"))
        ]
        
        mock_account_query = Mock()
        mock_session.query.side_effect = lambda model: mock_account_query if model == Account else mock_query
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = []
        
        response = client.get(
            "/api/v1/users/me/insights",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "data" in data
        assert "meta" in data
        
        # Check summary structure
        summary = data["data"]["summary"]
        assert "total_spending" in summary
        assert "average_daily_spend" in summary
        assert "top_category" in summary
        assert "savings_rate" in summary
        
        # Check charts structure
        charts = data["data"]["charts"]
        assert "spending_by_category" in charts
        assert "credit_utilization" in charts
        assert "subscriptions" in charts
        
        # Check subscriptions structure
        subscriptions = charts["subscriptions"]
        assert "total_monthly" in subscriptions
        assert "subscriptions" in subscriptions
        
        # Check meta structure
        meta = data["meta"]
        assert "timestamp" in meta
        assert "period" in meta
        assert "start_date" in meta
        assert "end_date" in meta
    
    @patch('app.api.v1.consumer.get_session')
    @patch('app.api.v1.consumer.require_consumer')
    def test_get_insights_subscription_detection(self, mock_require_consumer, mock_get_session, client, mock_consumer_user, mock_transactions):
        """Test subscription detection logic"""
        mock_require_consumer.return_value = mock_consumer_user
        
        mock_session = Mock(spec=Session)
        mock_get_session.return_value.__enter__.return_value = mock_session
        
        # Mock subscription merchant query
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.having.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.scalar.return_value = Decimal("195.48")
        mock_query.first.return_value = ("Subscriptions", Decimal("47.97"))
        
        # Mock subscription detection queries
        def query_side_effect(model):
            if model == Transaction:
                return mock_query
            return Mock()
        
        mock_session.query.side_effect = query_side_effect
        
        # Mock subscription merchants query result
        mock_query.all.return_value = [
            ("Netflix", Decimal("15.99"), 3)  # merchant, avg_amount, count
        ]
        
        # Mock individual merchant transaction query
        mock_merchant_query = Mock()
        mock_merchant_query.filter.return_value = mock_merchant_query
        mock_merchant_query.all.return_value = [
            (Decimal("-15.99"),),
            (Decimal("-15.99"),),
            (Decimal("-15.99"),)
        ]
        
        # Set up query chain for subscription detection
        def query_chain(model):
            if model == Transaction:
                return mock_query
            return Mock()
        
        mock_session.query.side_effect = query_chain
        
        # Mock account query
        mock_account_query = Mock()
        mock_session.query.side_effect = lambda model: mock_account_query if model == Account else mock_query
        mock_account_query.filter.return_value = mock_account_query
        mock_account_query.all.return_value = []
        
        response = client.get(
            "/api/v1/users/me/insights",
            headers={"Authorization": "Bearer mock-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        # Subscriptions should be detected
        assert "subscriptions" in data["data"]["charts"]

