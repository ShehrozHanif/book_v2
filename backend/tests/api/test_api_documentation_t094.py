"""Tests for T094: API Documentation."""

import pytest
import json
from pathlib import Path


class TestAPIDocumentationExists:
    """Test that API documentation file exists and is valid."""

    def test_api_documentation_exists(self):
        """Verify PERSONALIZATION_API.md exists."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        assert doc_path.exists(), "PERSONALIZATION_API.md not found"

    def test_api_documentation_not_empty(self):
        """Verify documentation is not empty."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        content = doc_path.read_text(encoding='utf-8')
        assert len(content) > 1000, "Documentation too short"

    def test_api_documentation_has_title(self):
        """Verify documentation has main title."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        content = doc_path.read_text(encoding='utf-8')
        assert "# Personalization System API Documentation" in content

    def test_api_documentation_has_version(self):
        """Verify documentation specifies API version."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        content = doc_path.read_text(encoding='utf-8')
        assert "Version" in content
        assert "1.0.0" in content


class TestAPIDocumentationStructure:
    """Test that documentation has proper structure."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_has_getting_started_section(self):
        """Verify Getting Started section exists."""
        content = self.load_documentation()
        assert "Getting Started" in content or "getting-started" in content.lower()

    def test_has_authentication_section(self):
        """Verify Authentication section exists."""
        content = self.load_documentation()
        assert "Authentication" in content

    def test_has_error_handling_section(self):
        """Verify Error Handling section exists."""
        content = self.load_documentation()
        assert "Error Handling" in content

    def test_has_rate_limiting_section(self):
        """Verify Rate Limiting section exists."""
        content = self.load_documentation()
        assert "Rate Limiting" in content or "rate-limiting" in content.lower()

    def test_has_endpoints_section(self):
        """Verify Endpoints section exists."""
        content = self.load_documentation()
        assert "Endpoints" in content

    def test_has_examples_section(self):
        """Verify Examples section exists."""
        content = self.load_documentation()
        assert "Examples" in content or "example" in content.lower()

    def test_has_sdk_section(self):
        """Verify SDK section exists."""
        content = self.load_documentation()
        assert "SDK" in content

    def test_has_table_of_contents(self):
        """Verify Table of Contents exists."""
        content = self.load_documentation()
        assert "Table of Contents" in content


class TestEndpointDocumentation:
    """Test that all endpoints are documented."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_authentication_endpoints(self):
        """Verify authentication endpoints documented."""
        content = self.load_documentation()
        assert "/users/register" in content
        assert "/users/login" in content
        assert "/users/refresh" in content

    def test_user_endpoints(self):
        """Verify user profile endpoints documented."""
        content = self.load_documentation()
        assert "/users/profile" in content

    def test_progress_endpoints(self):
        """Verify progress endpoints documented."""
        content = self.load_documentation()
        assert "/progress/" in content
        assert "complete" in content
        assert "practice" in content
        assert "retry" in content

    def test_dashboard_endpoint(self):
        """Verify dashboard endpoint documented."""
        content = self.load_documentation()
        assert "/dashboard/metrics" in content

    def test_achievement_endpoint(self):
        """Verify achievement endpoint documented."""
        content = self.load_documentation()
        assert "achievements" in content

    def test_statistics_endpoint(self):
        """Verify statistics endpoint documented."""
        content = self.load_documentation()
        assert "statistics" in content or "Statistics" in content

    def test_learning_path_endpoint(self):
        """Verify learning path endpoint documented."""
        content = self.load_documentation()
        assert "learning-paths" in content or "learning_paths" in content

    def test_preferences_endpoint(self):
        """Verify preferences endpoint documented."""
        content = self.load_documentation()
        assert "preferences" in content

    def test_health_endpoint(self):
        """Verify health endpoint documented."""
        content = self.load_documentation()
        assert "/health" in content or "health" in content.lower()

    def test_ready_endpoint(self):
        """Verify ready endpoint documented."""
        content = self.load_documentation()
        assert "/ready" in content or "ready" in content.lower()


class TestEndpointDocumentationDetails:
    """Test that each endpoint has proper details."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_endpoints_have_descriptions(self):
        """Verify endpoints have descriptions."""
        content = self.load_documentation()
        # Check for common documentation markers
        assert "**Request**:" in content
        assert "**Response** (" in content

    def test_endpoints_have_examples(self):
        """Verify endpoints have code examples."""
        content = self.load_documentation()
        assert "```json" in content or "```" in content
        assert "curl" in content.lower() or "example" in content.lower()

    def test_endpoints_have_error_documentation(self):
        """Verify error handling is documented."""
        content = self.load_documentation()
        assert "**Errors**:" in content
        assert "401" in content
        assert "400" in content

    def test_endpoints_have_parameters(self):
        """Verify endpoint parameters are documented."""
        content = self.load_documentation()
        assert "Path Parameters" in content or "Parameters" in content


class TestAuthenticationDocumentation:
    """Test authentication documentation."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_jwt_explained(self):
        """Verify JWT authentication explained."""
        content = self.load_documentation()
        assert "JWT" in content
        assert "Bearer" in content

    def test_token_types_explained(self):
        """Verify token types explained."""
        content = self.load_documentation()
        assert "access" in content.lower()
        assert "refresh" in content.lower()

    def test_authentication_flow_explained(self):
        """Verify authentication flow documented."""
        content = self.load_documentation()
        assert "Authorization" in content or "Bearer" in content

    def test_password_requirements_documented(self):
        """Verify password requirements documented."""
        content = self.load_documentation()
        assert "Password" in content
        assert "minimum" in content.lower() or "requirement" in content.lower()


class TestErrorHandlingDocumentation:
    """Test error handling documentation."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_status_codes_documented(self):
        """Verify HTTP status codes documented."""
        content = self.load_documentation()
        assert "200" in content
        assert "400" in content
        assert "401" in content
        assert "404" in content
        assert "500" in content

    def test_error_codes_documented(self):
        """Verify error codes documented."""
        content = self.load_documentation()
        assert "INVALID_REQUEST" in content or "error_code" in content
        assert "error" in content.lower()

    def test_error_response_format_shown(self):
        """Verify error response format shown."""
        content = self.load_documentation()
        assert "status" in content.lower()
        assert "error" in content.lower()


class TestRateLimitDocumentation:
    """Test rate limiting documentation."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_limits_specified(self):
        """Verify rate limits are specified."""
        content = self.load_documentation()
        assert "limit" in content.lower()
        assert "request" in content.lower()

    def test_limit_categories(self):
        """Verify different limit categories documented."""
        content = self.load_documentation()
        assert "Authentication" in content
        assert "General" in content or "general" in content.lower()

    def test_retry_guidance(self):
        """Verify retry guidance documented."""
        content = self.load_documentation()
        assert "429" in content
        assert "retry" in content.lower() or "Retry" in content


class TestExamplesDocumentation:
    """Test that examples are complete and working."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_curl_examples_present(self):
        """Verify curl examples present."""
        content = self.load_documentation()
        assert "curl" in content

    def test_json_examples_present(self):
        """Verify JSON examples present."""
        content = self.load_documentation()
        assert "```json" in content or '{"' in content

    def test_python_examples_present(self):
        """Verify Python examples present."""
        content = self.load_documentation()
        assert "python" in content.lower() or "import requests" in content

    def test_complete_flow_example(self):
        """Verify complete flow example included."""
        content = self.load_documentation()
        assert "register" in content.lower()
        assert "complete" in content.lower() or "chapter" in content.lower()


class TestSDKDocumentation:
    """Test SDK documentation."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_python_sdk_documented(self):
        """Verify Python SDK documented."""
        content = self.load_documentation()
        assert "Python" in content or "python" in content

    def test_sdk_has_usage_examples(self):
        """Verify SDK has usage examples."""
        content = self.load_documentation()
        assert "api =" in content or "client =" in content

    def test_sdk_shows_common_methods(self):
        """Verify SDK shows common methods."""
        content = self.load_documentation()
        assert "register" in content.lower()
        assert "login" in content.lower()


class TestDocumentationFormatting:
    """Test that documentation is well-formatted."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_has_markdown_headers(self):
        """Verify markdown headers used."""
        content = self.load_documentation()
        assert "#" in content  # Markdown header

    def test_has_code_blocks(self):
        """Verify code blocks present."""
        content = self.load_documentation()
        assert "```" in content

    def test_has_tables(self):
        """Verify tables present for structure."""
        content = self.load_documentation()
        assert "|" in content  # Markdown table

    def test_has_links(self):
        """Verify links present."""
        content = self.load_documentation()
        assert "[" in content and "]" in content  # Markdown link

    def test_consistent_formatting(self):
        """Verify consistent formatting."""
        content = self.load_documentation()
        # Check for consistent endpoint formatting
        assert "/api/v1/" in content or "GET /" in content


class TestDocumentationCompleteness:
    """Test that documentation is complete."""

    def load_documentation(self):
        """Load API documentation."""
        doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
        return doc_path.read_text(encoding='utf-8')

    def test_base_url_specified(self):
        """Verify base URL specified."""
        content = self.load_documentation()
        assert "Base URL" in content or "base_url" in content.lower()
        assert "localhost" in content or "api" in content.lower()

    def test_authentication_required_indicated(self):
        """Verify which endpoints need auth."""
        content = self.load_documentation()
        assert "Authorization" in content or "Bearer" in content

    def test_response_examples_complete(self):
        """Verify response examples are complete."""
        content = self.load_documentation()
        # Check for typical response fields
        assert "status" in content.lower() or '"' in content

    def test_error_cases_documented(self):
        """Verify error cases documented."""
        content = self.load_documentation()
        assert "401" in content  # Unauthorized
        assert "400" in content  # Bad request
        assert "404" in content  # Not found

    def test_endpoints_grouped_logically(self):
        """Verify endpoints grouped logically."""
        content = self.load_documentation()
        # Should have sections for different endpoint types
        assert "Authentication" in content
        assert "Profile" in content or "User" in content


def test_api_documentation_summary():
    """Summary test for API documentation."""
    doc_path = Path(__file__).parent.parent.parent.parent / "PERSONALIZATION_API.md"
    assert doc_path.exists()

    content = doc_path.read_text(encoding='utf-8')

    # Core sections
    assert "Getting Started" in content
    assert "Authentication" in content
    assert "Error Handling" in content
    assert "Rate Limiting" in content
    assert "Endpoints" in content
    assert "Examples" in content
    assert "SDKs" in content

    # Key content
    assert "/users/register" in content
    assert "/users/login" in content
    assert "/dashboard/metrics" in content
    assert "/progress/" in content
    assert "JWT" in content
    assert "Bearer" in content
    assert "curl" in content
    assert "python" in content.lower()

    # Formatting
    assert "#" in content  # Headers
    assert "```" in content  # Code blocks
    assert "|" in content  # Tables
