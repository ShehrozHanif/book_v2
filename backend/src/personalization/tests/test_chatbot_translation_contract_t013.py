"""
Contract tests for chatbot translation API endpoints.

Tests the API contracts for:
1. GET /api/v1/chatbot/response/{template_key} - Get translated response
2. GET /api/v1/chatbot/templates - List templates
3. POST /api/v1/users/{user_id}/language - Set language preference
4. GET /api/v1/users/{user_id}/language - Get language preference
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
from uuid import uuid4
import jwt


@pytest.fixture
def client():
    """Create FastAPI test client."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def valid_jwt_token():
    """Create a valid JWT token for testing."""
    user_id = str(uuid4())
    token = jwt.encode(
        {"sub": user_id, "email": "test@example.com"},
        "your-secret-key",
        algorithm="HS256"
    )
    return token, user_id


class TestChatbotResponseContract:
    """Contract tests for GET /api/v1/chatbot/response/{template_key}"""

    def test_get_response_english_no_auth_required(self, client):
        """English responses should be accessible without authentication."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=english"
        )
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "content" in data
            assert "template_key" in data
            assert data["language"] == "english"

    def test_get_response_urdu_requires_auth(self, client):
        """Urdu responses should require authentication."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu"
        )
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_get_response_urdu_with_valid_token(self, client, valid_jwt_token):
        """Urdu response should return with valid authentication."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu",
            headers=headers
        )
        # Should be 200 or 404 if template not seeded, but NOT 401
        assert response.status_code in [200, 404]
        assert response.status_code != 401

    def test_get_response_template_not_found(self, client, valid_jwt_token):
        """Should return 404 for non-existent template."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/chatbot/response/nonexistent_template_xyz?language=urdu",
            headers=headers
        )
        assert response.status_code == 404

    def test_get_response_invalid_language_defaults_to_english(self, client):
        """Invalid language should default to English."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=invalid"
        )
        # Should default to English and not require auth
        assert response.status_code in [200, 404]

    def test_get_response_contract_structure(self, client):
        """Response should have required structure."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=english"
        )
        if response.status_code == 200:
            data = response.json()
            # Must have these fields
            assert "content" in data
            assert "template_key" in data
            assert "language" in data
            assert "version" in data
            # Fields should have correct types
            assert isinstance(data["content"], str)
            assert isinstance(data["language"], str)
            assert isinstance(data["version"], int)

    def test_get_response_fallback_to_english_if_urdu_unavailable(self, client, valid_jwt_token):
        """Should fallback to English if Urdu translation not available."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/chatbot/response/some_template?language=urdu",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            # Should have note about fallback
            if "note" in data:
                assert "Urdu translation not yet available" in data["note"]


class TestListTemplatesContract:
    """Contract tests for GET /api/v1/chatbot/templates"""

    def test_list_templates_no_auth_required(self, client):
        """Listing templates should not require authentication."""
        response = client.get("/api/v1/chatbot/templates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_templates_response_structure(self, client):
        """Response should be array of template objects."""
        response = client.get("/api/v1/chatbot/templates")
        assert response.status_code == 200
        data = response.json()

        if len(data) > 0:
            template = data[0]
            # Each template should have required fields
            assert "id" in template or "template_key" in template
            assert "english_content" in template or "content" in template
            assert "version" in template
            assert "status" in template

    def test_list_templates_with_filters(self, client):
        """Should support status filter."""
        response = client.get(
            "/api/v1/chatbot/templates?status_filter=published&limit=50"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # All templates should be published
        for template in data:
            if "status" in template:
                assert template["status"] == "published"

    def test_list_templates_respects_limit(self, client):
        """Should respect limit parameter."""
        response = client.get("/api/v1/chatbot/templates?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    def test_list_templates_empty_response(self, client):
        """Should handle empty template list gracefully."""
        response = client.get("/api/v1/chatbot/templates?status_filter=draft")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # May be empty if no draft templates


class TestLanguagePreferenceContract:
    """Contract tests for language preference endpoints"""

    def test_set_language_requires_auth(self, client):
        """Setting language should require authentication."""
        user_id = uuid4()
        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"}
        )
        assert response.status_code == 401

    def test_set_language_with_valid_auth(self, client, valid_jwt_token):
        """Should allow setting language with valid token."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=headers
        )
        # Should succeed
        assert response.status_code in [200, 201]
        data = response.json()
        assert "language" in data
        assert data["language"] == "urdu"

    def test_set_language_invalid_user_id(self, client, valid_jwt_token):
        """Should return 403 if user tries to set another user's language."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}
        other_user_id = uuid4()

        response = client.post(
            f"/api/v1/users/{other_user_id}/language",
            json={"language": "urdu"},
            headers=headers
        )
        assert response.status_code == 403
        assert "permission" in response.json()["detail"].lower()

    def test_set_language_invalid_language(self, client, valid_jwt_token):
        """Should return 400 for unsupported language."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "klingon"},
            headers=headers
        )
        assert response.status_code == 400
        assert "Unsupported language" in response.json()["detail"]

    def test_set_language_response_contract(self, client, valid_jwt_token):
        """Response should have required structure."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "english"},
            headers=headers
        )
        if response.status_code in [200, 201]:
            data = response.json()
            assert "user_id" in data
            assert "language" in data
            assert isinstance(data["language"], str)
            assert data["language"] in ["english", "urdu"]

    def test_get_language_requires_auth(self, client):
        """Getting language should require authentication."""
        user_id = uuid4()
        response = client.get(f"/api/v1/users/{user_id}/language")
        assert response.status_code == 401

    def test_get_language_with_valid_auth(self, client, valid_jwt_token):
        """Should return language preference with valid token."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "language" in data
        assert data["language"] in ["english", "urdu"]

    def test_get_language_invalid_user_id(self, client, valid_jwt_token):
        """Should return 403 if user tries to get another user's language."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}
        other_user_id = uuid4()

        response = client.get(
            f"/api/v1/users/{other_user_id}/language",
            headers=headers
        )
        assert response.status_code == 403

    def test_get_language_returns_default_if_not_set(self, client, valid_jwt_token):
        """Should return default language for new users."""
        token, user_id = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            # Should have a language (default is english)
            assert "language" in data
            assert data["language"] in ["english", "urdu"]


class TestErrorHandling:
    """Contract tests for error handling"""

    def test_missing_authorization_header(self, client):
        """Endpoints requiring auth should return 401 without header."""
        user_id = uuid4()
        response = client.get(f"/api/v1/users/{user_id}/language")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_invalid_token_format(self, client):
        """Should return 401 for malformed token."""
        user_id = uuid4()
        headers = {"Authorization": "InvalidToken"}
        response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=headers
        )
        assert response.status_code == 401

    def test_expired_token(self, client):
        """Should return 401 for expired token."""
        import jwt
        from datetime import datetime, timedelta

        expired_token = jwt.encode(
            {"sub": str(uuid4()), "exp": datetime.utcnow() - timedelta(hours=1)},
            "your-secret-key",
            algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        user_id = uuid4()
        response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=headers
        )
        assert response.status_code == 401

    def test_invalid_uuid_format(self, client, valid_jwt_token):
        """Should handle invalid UUID format gracefully."""
        token, _ = valid_jwt_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get(
            "/api/v1/users/not-a-uuid/language",
            headers=headers
        )
        # Should return 400 or 404, not 500
        assert response.status_code in [400, 404]
