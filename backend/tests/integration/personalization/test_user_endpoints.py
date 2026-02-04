"""Integration tests for user authentication endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from uuid import UUID

from src.main import app
from src.personalization.models.db_models import Base, User
from src.personalization.utils.auth import init_auth_config
from src.database.connection import get_session


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine and session
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    """Override database dependency for testing."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def setup_database():
    """Setup test database before each test."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize auth config
    init_auth_config(
        secret_key="test_secret_key_minimum_32_chars_long_for_security",
        access_expire=30,
        refresh_expire=7
    )

    yield

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(setup_database):
    """Create test client with database override."""
    app.dependency_overrides[get_session] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def db_session(setup_database):
    """Get database session for tests."""
    async with TestSessionLocal() as session:
        yield session


@pytest.mark.asyncio
class TestUserRegistration:
    """Tests for user registration endpoint."""

    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 201
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"
        assert "user_id" in data

        # Validate user_id is a valid UUID
        UUID(data["user_id"])

    async def test_register_user_duplicate_username(self, client: AsyncClient):
        """Test registration with duplicate username fails."""
        user_data = {
            "username": "duplicateuser",
            "email": "user1@example.com",
            "password": "SecurePass123!"
        }

        # First registration
        response1 = await client.post("/api/v1/users/register", json=user_data)
        assert response1.status_code == 201

        # Try to register with same username but different email
        user_data["email"] = "user2@example.com"
        response2 = await client.post("/api/v1/users/register", json=user_data)

        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    async def test_register_user_duplicate_email(self, client: AsyncClient):
        """Test registration with duplicate email fails."""
        user_data1 = {
            "username": "user1",
            "email": "duplicate@example.com",
            "password": "SecurePass123!"
        }

        # First registration
        response1 = await client.post("/api/v1/users/register", json=user_data1)
        assert response1.status_code == 201

        # Try to register with same email but different username
        user_data2 = {
            "username": "user2",
            "email": "duplicate@example.com",
            "password": "SecurePass456!"
        }
        response2 = await client.post("/api/v1/users/register", json=user_data2)

        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()

    async def test_register_user_weak_password(self, client: AsyncClient):
        """Test registration with weak password fails."""
        user_data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak"
        }

        response = await client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 400
        assert "password" in response.json()["detail"].lower()

    async def test_register_user_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email fails."""
        user_data = {
            "username": "invalidemailuser",
            "email": "not-an-email",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 422  # Validation error

    async def test_register_user_short_username(self, client: AsyncClient):
        """Test registration with too short username fails."""
        user_data = {
            "username": "ab",  # Too short (min 3)
            "email": "short@example.com",
            "password": "SecurePass123!"
        }

        response = await client.post("/api/v1/users/register", json=user_data)

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestUserLogin:
    """Tests for user login endpoint."""

    async def test_login_success(self, client: AsyncClient):
        """Test successful user login."""
        # Register user first
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        await client.post("/api/v1/users/register", json=user_data)

        # Login
        login_data = {
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        response = await client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "loginuser"

    async def test_login_wrong_password(self, client: AsyncClient):
        """Test login with wrong password fails."""
        # Register user
        user_data = {
            "username": "wrongpassuser",
            "email": "wrongpass@example.com",
            "password": "CorrectPass123!"
        }
        await client.post("/api/v1/users/register", json=user_data)

        # Try login with wrong password
        login_data = {
            "email": "wrongpass@example.com",
            "password": "WrongPass123!"
        }
        response = await client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user fails."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePass123!"
        }
        response = await client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()

    async def test_login_case_insensitive_email(self, client: AsyncClient):
        """Test login with different email case works."""
        # Register with lowercase email
        user_data = {
            "username": "caseuser",
            "email": "case@example.com",
            "password": "SecurePass123!"
        }
        await client.post("/api/v1/users/register", json=user_data)

        # Login with uppercase email
        login_data = {
            "email": "CASE@EXAMPLE.COM",
            "password": "SecurePass123!"
        }
        response = await client.post("/api/v1/users/login", json=login_data)

        assert response.status_code == 200


@pytest.mark.asyncio
class TestTokenRefresh:
    """Tests for token refresh endpoint."""

    async def test_refresh_token_success(self, client: AsyncClient):
        """Test successful token refresh."""
        # Register and get tokens
        user_data = {
            "username": "refreshuser",
            "email": "refresh@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        refresh_token = tokens["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/users/refresh",
            params={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["access_token"] != tokens["access_token"]  # New token

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token fails."""
        response = await client.post(
            "/api/v1/users/refresh",
            params={"refresh_token": "invalid.token.here"}
        )

        assert response.status_code == 401

    async def test_refresh_with_access_token_fails(self, client: AsyncClient):
        """Test refresh with access token instead of refresh token fails."""
        # Register and get tokens
        user_data = {
            "username": "accesstokenuser",
            "email": "accesstoken@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Try to use access token for refresh
        response = await client.post(
            "/api/v1/users/refresh",
            params={"refresh_token": access_token}
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetCurrentUser:
    """Tests for get current user endpoint."""

    async def test_get_current_user_success(self, client: AsyncClient):
        """Test getting current user profile."""
        # Register user
        user_data = {
            "username": "currentuser",
            "email": "current@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "currentuser"
        assert data["email"] == "current@example.com"
        assert data["skill_level"] == 50  # Default
        assert data["skill_confidence"] == 50  # Default
        assert "preferences" in data
        assert data["preferences"]["code_language"] == "python"

    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Test getting current user without token fails."""
        response = await client.get("/api/v1/users/me")

        assert response.status_code == 401

    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Test getting current user with invalid token fails."""
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token"}
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestUpdateUserProfile:
    """Tests for update user profile endpoint."""

    async def test_update_username(self, client: AsyncClient):
        """Test updating username."""
        # Register user
        user_data = {
            "username": "oldusername",
            "email": "update@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Update username
        update_data = {"username": "newusername"}
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newusername"

    async def test_update_bio(self, client: AsyncClient):
        """Test updating user bio."""
        # Register user
        user_data = {
            "username": "biouser",
            "email": "bio@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Update bio
        update_data = {"bio": "Robotics enthusiast learning about humanoid robots"}
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["bio"] == "Robotics enthusiast learning about humanoid robots"

    async def test_update_preferences(self, client: AsyncClient):
        """Test updating user preferences."""
        # Register user
        user_data = {
            "username": "prefuser",
            "email": "pref@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Update preferences
        update_data = {
            "preferences": {
                "explanation_style": "theory_first",
                "code_language": "cpp",
                "learning_pace": "fast",
                "content_focus": "hardware"
            }
        }
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["preferences"]["explanation_style"] == "theory_first"
        assert data["preferences"]["code_language"] == "cpp"
        assert data["preferences"]["learning_pace"] == "fast"

    async def test_update_to_duplicate_username_fails(self, client: AsyncClient):
        """Test updating to existing username fails."""
        # Register two users
        user1 = {
            "username": "user1",
            "email": "user1@example.com",
            "password": "SecurePass123!"
        }
        user2 = {
            "username": "user2",
            "email": "user2@example.com",
            "password": "SecurePass123!"
        }
        await client.post("/api/v1/users/register", json=user1)
        reg_response = await client.post("/api/v1/users/register", json=user2)
        tokens = reg_response.json()
        access_token = tokens["access_token"]

        # Try to update user2's username to user1
        update_data = {"username": "user1"}
        response = await client.put(
            "/api/v1/users/me",
            json=update_data,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
class TestGetUserById:
    """Tests for get user by ID endpoint."""

    async def test_get_user_by_id_success(self, client: AsyncClient):
        """Test getting user by ID."""
        # Register user
        user_data = {
            "username": "iduser",
            "email": "iduser@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        tokens = reg_response.json()
        user_id = tokens["user_id"]
        access_token = tokens["access_token"]

        # Get user by ID
        response = await client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["username"] == "iduser"

    async def test_get_user_by_id_not_found(self, client: AsyncClient):
        """Test getting non-existent user returns 404."""
        # Register user for auth
        user_data = {
            "username": "authuser",
            "email": "auth@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        access_token = reg_response.json()["access_token"]

        # Try to get non-existent user
        fake_uuid = "123e4567-e89b-12d3-a456-426614174999"
        response = await client.get(
            f"/api/v1/users/{fake_uuid}",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 404

    async def test_get_user_by_id_requires_auth(self, client: AsyncClient):
        """Test getting user by ID requires authentication."""
        fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
        response = await client.get(f"/api/v1/users/{fake_uuid}")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestLogout:
    """Tests for logout endpoint."""

    async def test_logout_success(self, client: AsyncClient):
        """Test successful logout."""
        # Register user
        user_data = {
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "SecurePass123!"
        }
        reg_response = await client.post("/api/v1/users/register", json=user_data)
        access_token = reg_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/api/v1/users/logout",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 204

    async def test_logout_requires_auth(self, client: AsyncClient):
        """Test logout requires authentication."""
        response = await client.post("/api/v1/users/logout")

        assert response.status_code == 401
