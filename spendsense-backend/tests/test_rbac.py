"""Unit tests for role-based access control"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.dependencies import get_current_user, require_role, require_operator, require_consumer
from app.utils.models import UserInfo
from app.main import app


# Mock JWT tokens (base64 encoded JSON)
MOCK_TOKEN_CONSUMER = "mock.consumer.token"
MOCK_TOKEN_OPERATOR = "mock.operator.token"
MOCK_TOKEN_NO_ROLE = "mock.no.role.token"


@pytest.fixture
def mock_consumer_user():
    """Mock consumer user info"""
    return UserInfo(
        user_id="test-user-id",
        role="consumer",
        email="consumer@test.com"
    )


@pytest.fixture
def mock_operator_user():
    """Mock operator user info"""
    return UserInfo(
        user_id="test-operator-id",
        role="operator",
        email="operator@test.com"
    )


class TestRoleExtraction:
    """Test role extraction from JWT claims"""
    
    def test_extract_role_from_groups_operators(self):
        """Test extracting operator role from cognito:groups"""
        from app.utils.jwt import extract_role_from_claims
        
        claims = {"cognito:groups": ["operators"]}
        role = extract_role_from_claims(claims)
        assert role == "operator"
    
    def test_extract_role_from_groups_consumers(self):
        """Test extracting consumer role from cognito:groups"""
        from app.utils.jwt import extract_role_from_claims
        
        claims = {"cognito:groups": ["consumers"]}
        role = extract_role_from_claims(claims)
        assert role == "consumer"
    
    def test_extract_role_from_custom_role(self):
        """Test extracting role from custom:role claim"""
        from app.utils.jwt import extract_role_from_claims
        
        claims = {"custom:role": "operator"}
        role = extract_role_from_claims(claims)
        assert role == "operator"
    
    def test_extract_role_defaults_to_consumer(self):
        """Test default role is consumer when no role info"""
        from app.utils.jwt import extract_role_from_claims
        
        claims = {"sub": "test-user"}
        role = extract_role_from_claims(claims)
        assert role == "consumer"
    
    def test_extract_role_operators_priority_over_consumers(self):
        """Test operators group takes priority over consumers"""
        from app.utils.jwt import extract_role_from_claims
        
        claims = {"cognito:groups": ["consumers", "operators"]}
        role = extract_role_from_claims(claims)
        assert role == "operator"


class TestRequireRole:
    """Test require_role dependency"""
    
    @pytest.mark.asyncio
    async def test_require_role_consumer_success(self, mock_consumer_user):
        """Test require_role allows consumer when required"""
        with patch('app.dependencies.get_current_user', return_value=mock_consumer_user):
            dependency = require_role("consumer")
            result = await dependency(mock_consumer_user)
            assert result.role == "consumer"
    
    @pytest.mark.asyncio
    async def test_require_role_operator_success(self, mock_operator_user):
        """Test require_role allows operator when required"""
        with patch('app.dependencies.get_current_user', return_value=mock_operator_user):
            dependency = require_role("operator")
            result = await dependency(mock_operator_user)
            assert result.role == "operator"
    
    @pytest.mark.asyncio
    async def test_require_role_consumer_rejects_operator(self, mock_operator_user):
        """Test require_role rejects operator when consumer required"""
        with patch('app.dependencies.get_current_user', return_value=mock_operator_user):
            dependency = require_role("consumer")
            with pytest.raises(HTTPException) as exc_info:
                await dependency(mock_operator_user)
            assert exc_info.value.status_code == 403
    
    @pytest.mark.asyncio
    async def test_require_role_operator_rejects_consumer(self, mock_consumer_user):
        """Test require_role rejects consumer when operator required"""
        with patch('app.dependencies.get_current_user', return_value=mock_consumer_user):
            dependency = require_role("operator")
            with pytest.raises(HTTPException) as exc_info:
                await dependency(mock_consumer_user)
            assert exc_info.value.status_code == 403


class TestRequireOperator:
    """Test require_operator dependency"""
    
    @pytest.mark.asyncio
    async def test_require_operator_success(self, mock_operator_user):
        """Test require_operator allows operator"""
        result = await require_operator(mock_operator_user)
        assert result.role == "operator"
    
    @pytest.mark.asyncio
    async def test_require_operator_rejects_consumer(self, mock_consumer_user):
        """Test require_operator rejects consumer"""
        with pytest.raises(HTTPException) as exc_info:
            await require_operator(mock_consumer_user)
        assert exc_info.value.status_code == 403
        assert "Operator role required" in str(exc_info.value.detail)


class TestRequireConsumer:
    """Test require_consumer dependency"""
    
    @pytest.mark.asyncio
    async def test_require_consumer_allows_consumer(self, mock_consumer_user):
        """Test require_consumer allows consumer"""
        result = await require_consumer(mock_consumer_user)
        assert result.role == "consumer"
    
    @pytest.mark.asyncio
    async def test_require_consumer_allows_operator(self, mock_operator_user):
        """Test require_consumer allows operator (consumer endpoints allow all authenticated users)"""
        result = await require_consumer(mock_operator_user)
        assert result.role == "operator"


class TestProtectedEndpoints:
    """Integration tests for protected endpoints"""
    
    def test_consumer_endpoint_without_auth(self):
        """Test consumer endpoint without authentication returns 401"""
        client = TestClient(app)
        response = client.get("/api/v1/users/me/profile")
        assert response.status_code == 401
    
    def test_operator_endpoint_without_auth(self):
        """Test operator endpoint without authentication returns 401"""
        client = TestClient(app)
        response = client.get("/api/v1/operator/users")
        assert response.status_code == 401
    
    @patch('app.dependencies.get_current_user')
    def test_consumer_endpoint_with_consumer_role(self, mock_get_user, mock_consumer_user):
        """Test consumer endpoint with consumer role succeeds"""
        mock_get_user.return_value = mock_consumer_user
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/users/me/profile",
            headers={"Authorization": f"Bearer {MOCK_TOKEN_CONSUMER}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "consumer"
    
    @patch('app.dependencies.get_current_user')
    def test_consumer_endpoint_with_operator_role(self, mock_get_user, mock_operator_user):
        """Test consumer endpoint with operator role succeeds (consumer endpoints allow all)"""
        mock_get_user.return_value = mock_operator_user
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/users/me/profile",
            headers={"Authorization": f"Bearer {MOCK_TOKEN_OPERATOR}"}
        )
        assert response.status_code == 200
    
    @patch('app.dependencies.get_current_user')
    def test_operator_endpoint_with_consumer_role(self, mock_get_user, mock_consumer_user):
        """Test operator endpoint with consumer role returns 403"""
        mock_get_user.return_value = mock_consumer_user
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/operator/users",
            headers={"Authorization": f"Bearer {MOCK_TOKEN_CONSUMER}"}
        )
        assert response.status_code == 403
    
    @patch('app.dependencies.get_current_user')
    def test_operator_endpoint_with_operator_role(self, mock_get_user, mock_operator_user):
        """Test operator endpoint with operator role succeeds"""
        mock_get_user.return_value = mock_operator_user
        
        client = TestClient(app)
        response = client.get(
            "/api/v1/operator/users",
            headers={"Authorization": f"Bearer {MOCK_TOKEN_OPERATOR}"}
        )
        assert response.status_code == 200

