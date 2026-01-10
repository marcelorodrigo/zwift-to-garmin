"""Tests for Zwift API request module."""

import pytest
import requests
import responses

from services.zwift.request import ZwiftApiRequest, ZwiftApiError


class TestZwiftApiRequest:
    """Tests for ZwiftApiRequest class."""

    @pytest.fixture
    def api_request(self):
        """Create a ZwiftApiRequest instance for testing."""
        return ZwiftApiRequest(lambda: "test_token")

    @responses.activate
    def test_get_json_success(self, api_request):
        """Test successful JSON API request."""
        # Given
        expected_data = {"id": 12345, "name": "Test User"}
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json=expected_data,
            status=200,
        )

        # When
        result = api_request.get_json("/api/profiles/me")

        # Then
        assert result == expected_data
        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers["Authorization"] == "Bearer test_token"
        assert responses.calls[0].request.headers["Accept"] == "application/json"

    @responses.activate
    def test_get_json_http_error(self, api_request):
        """Test handling of HTTP errors."""
        # Given
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"error": "not found"},
            status=404,
        )

        # When & Then
        with pytest.raises(ZwiftApiError, match="API request failed: 404"):
            api_request.get_json("/api/profiles/me")

    @responses.activate
    def test_get_json_network_error(self, api_request):
        """Test handling of network errors."""
        # Given
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            body=requests.exceptions.ConnectionError("Connection refused"),
        )

        # When & Then
        with pytest.raises(ZwiftApiError, match="Failed to connect"):
            api_request.get_json("/api/profiles/me")

    def test_get_headers_includes_authorization(self, api_request):
        """Test that headers include authorization token."""
        headers = api_request._get_headers()
        assert headers["Authorization"] == "Bearer test_token"
        assert headers["Accept"] == "application/json"
        assert "User-Agent" in headers
