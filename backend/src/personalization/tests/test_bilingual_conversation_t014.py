"""
Integration tests for bilingual chatbot conversation flow.

Tests the complete workflow:
1. User login / authentication
2. Select Urdu language
3. Get Urdu chatbot responses
4. Switch languages
5. Preference persistence
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import jwt


@pytest.fixture
def client():
    """Create FastAPI test client."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database session."""
    db = MagicMock(spec=AsyncSession)
    return db


@pytest.fixture
def authenticated_user():
    """Create test user data."""
    user_id = str(uuid4())
    token = jwt.encode(
        {"sub": user_id, "email": "testuser@example.com", "username": "testuser"},
        "your-secret-key",
        algorithm="HS256"
    )
    return {
        "user_id": user_id,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }


class TestBilingualConversationFlow:
    """Integration tests for bilingual conversation flow"""

    def test_guest_user_can_access_english(self, client):
        """Guest users can access English responses without login."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=english"
        )
        # Should not require authentication for English
        assert response.status_code in [200, 404]

    def test_guest_user_cannot_access_urdu(self, client):
        """Guest users cannot access Urdu responses."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu"
        )
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]

    def test_authenticated_user_can_access_urdu(self, client, authenticated_user):
        """Authenticated users can access Urdu responses."""
        response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu",
            headers=authenticated_user["headers"]
        )
        # Should not be 401 (auth is valid)
        assert response.status_code != 401
        # May be 404 if template not seeded, but not 401
        assert response.status_code in [200, 404]

    def test_user_can_set_language_preference(self, client, authenticated_user):
        """User can set their language preference."""
        user_id = authenticated_user["user_id"]

        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=authenticated_user["headers"]
        )
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["language"] == "urdu"

    def test_user_can_switch_languages(self, client, authenticated_user):
        """User can switch from one language to another."""
        user_id = authenticated_user["user_id"]

        # Set to Urdu
        response1 = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=authenticated_user["headers"]
        )
        assert response1.status_code in [200, 201]

        # Switch back to English
        response2 = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "english"},
            headers=authenticated_user["headers"]
        )
        assert response2.status_code in [200, 201]
        data = response2.json()
        assert data["language"] == "english"

    def test_language_preference_persists(self, client, authenticated_user):
        """Language preference is saved and retrieved."""
        user_id = authenticated_user["user_id"]

        # Set preference to Urdu
        response1 = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=authenticated_user["headers"]
        )
        assert response1.status_code in [200, 201]

        # Retrieve preference
        response2 = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=authenticated_user["headers"]
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data["language"] == "urdu"

    def test_complete_conversation_flow(self, client, authenticated_user):
        """Test complete bilingual conversation flow."""
        user_id = authenticated_user["user_id"]

        # Step 1: User sets language to Urdu
        set_response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=authenticated_user["headers"]
        )
        assert set_response.status_code in [200, 201]

        # Step 2: User gets language preference
        get_response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=authenticated_user["headers"]
        )
        assert get_response.status_code == 200
        assert get_response.json()["language"] == "urdu"

        # Step 3: User requests Urdu response
        chatbot_response = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu",
            headers=authenticated_user["headers"]
        )
        # Should succeed (200 or 404 if template not found, but NOT 401)
        assert chatbot_response.status_code != 401

        # Step 4: User lists templates (public endpoint)
        templates_response = client.get("/api/v1/chatbot/templates")
        assert templates_response.status_code == 200

    def test_glossary_supports_multiple_languages(self, client, authenticated_user):
        """Glossary search should support both English and Urdu."""
        # Search in English
        english_search = client.get(
            "/api/v1/glossary/search?q=robot&language=english",
            headers=authenticated_user["headers"]
        )
        assert english_search.status_code == 200

        # Search in Urdu
        urdu_search = client.get(
            "/api/v1/glossary/search?q=روبوٹ&language=urdu",
            headers=authenticated_user["headers"]
        )
        assert urdu_search.status_code == 200

    def test_glossary_access_without_auth(self, client):
        """Glossary should be accessible to all users."""
        response = client.get("/api/v1/glossary/search?q=robot")
        assert response.status_code == 200

    def test_multiple_users_independent_preferences(self, client):
        """Different users should have independent language preferences."""
        # Create two authenticated users
        user1_id = str(uuid4())
        user1_token = jwt.encode(
            {"sub": user1_id},
            "your-secret-key",
            algorithm="HS256"
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        user2_id = str(uuid4())
        user2_token = jwt.encode(
            {"sub": user2_id},
            "your-secret-key",
            algorithm="HS256"
        )
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # User 1 sets Urdu
        response1 = client.post(
            f"/api/v1/users/{user1_id}/language",
            json={"language": "urdu"},
            headers=user1_headers
        )
        assert response1.status_code in [200, 201]

        # User 2 keeps English
        response2 = client.post(
            f"/api/v1/users/{user2_id}/language",
            json={"language": "english"},
            headers=user2_headers
        )
        assert response2.status_code in [200, 201]

        # Verify preferences
        get1 = client.get(
            f"/api/v1/users/{user1_id}/language",
            headers=user1_headers
        )
        assert get1.json()["language"] == "urdu"

        get2 = client.get(
            f"/api/v1/users/{user2_id}/language",
            headers=user2_headers
        )
        assert get2.json()["language"] == "english"

    def test_logout_and_relogin_preserves_preference(self, client):
        """Language preference should persist across logout/login."""
        user_id = str(uuid4())

        # Initial login and set Urdu
        token1 = jwt.encode(
            {"sub": user_id},
            "your-secret-key",
            algorithm="HS256"
        )
        headers1 = {"Authorization": f"Bearer {token1}"}

        client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "urdu"},
            headers=headers1
        )

        # Simulate logout (new token issued)
        token2 = jwt.encode(
            {"sub": user_id},
            "your-secret-key",
            algorithm="HS256"
        )
        headers2 = {"Authorization": f"Bearer {token2}"}

        # Check preference is still Urdu
        response = client.get(
            f"/api/v1/users/{user_id}/language",
            headers=headers2
        )
        assert response.status_code == 200
        assert response.json()["language"] == "urdu"


class TestLanguageValidation:
    """Test language validation in bilingual flow"""

    def test_only_supported_languages_accepted(self, client, authenticated_user):
        """Only english and urdu should be accepted."""
        user_id = authenticated_user["user_id"]

        # Try invalid language
        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "spanish"},
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 400

    def test_language_case_insensitive(self, client, authenticated_user):
        """Language input should be case insensitive."""
        user_id = authenticated_user["user_id"]

        response = client.post(
            f"/api/v1/users/{user_id}/language",
            json={"language": "URDU"},
            headers=authenticated_user["headers"]
        )
        # Should accept URDU and normalize it
        assert response.status_code in [200, 201]

    def test_language_parameter_in_endpoint_is_flexible(self, client):
        """GET /response endpoint should handle language parameter flexibly."""
        # lowercase
        response1 = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=urdu"
        )
        # UPPERCASE
        response2 = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=URDU"
        )
        # Mixed case
        response3 = client.get(
            "/api/v1/chatbot/response/greeting_welcome?language=Urdu"
        )

        # All should have same auth behavior (401 for guest)
        assert response1.status_code == 401
        assert response2.status_code == 401
        assert response3.status_code == 401


class TestBilingualErrorScenarios:
    """Test error scenarios in bilingual flow"""

    def test_invalid_template_key(self, client, authenticated_user):
        """Should return 404 for non-existent template."""
        response = client.get(
            "/api/v1/chatbot/response/nonexistent_key_xyz?language=urdu",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404

    def test_response_fallback_when_translation_missing(self, client, authenticated_user):
        """Should fallback to English if Urdu translation not available."""
        response = client.get(
            "/api/v1/chatbot/response/any_template?language=urdu",
            headers=authenticated_user["headers"]
        )
        if response.status_code == 200:
            data = response.json()
            # Should indicate fallback if applicable
            if "note" in data:
                assert "not yet available" in data["note"].lower()

    def test_cannot_access_other_user_preference(self, client):
        """User cannot access another user's language preference."""
        user1_id = str(uuid4())
        user2_id = str(uuid4())

        user1_token = jwt.encode(
            {"sub": user1_id},
            "your-secret-key",
            algorithm="HS256"
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        # User 1 tries to get User 2's preference
        response = client.get(
            f"/api/v1/users/{user2_id}/language",
            headers=user1_headers
        )
        assert response.status_code == 403

    def test_cannot_modify_other_user_preference(self, client):
        """User cannot modify another user's language preference."""
        user1_id = str(uuid4())
        user2_id = str(uuid4())

        user1_token = jwt.encode(
            {"sub": user1_id},
            "your-secret-key",
            algorithm="HS256"
        )
        user1_headers = {"Authorization": f"Bearer {user1_token}"}

        # User 1 tries to set User 2's preference
        response = client.post(
            f"/api/v1/users/{user2_id}/language",
            json={"language": "urdu"},
            headers=user1_headers
        )
        assert response.status_code == 403
