"""Tests for Zwift authentication module."""

import time
import pytest
import requests
import responses

from services.zwift.auth import ZwiftAuth, ZwiftAuthError


class TestZwiftAuth:
    """Tests for ZwiftAuth class."""

    @pytest.fixture
    def auth(self):
        """Create a ZwiftAuth instance for testing."""
        return ZwiftAuth("test@example.com", "testpassword")

    @responses.activate
    def test_get_access_token_password_grant(self, auth):
        """Test initial authentication with password grant."""
        # Given
        token_response = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "refresh_expires_in": 86400,
        }
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json=token_response,
            status=200,
        )

        # When
        token = auth.get_access_token()

        # Then
        assert token == "test_access_token"
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        assert "grant_type=password" in request_body
        assert "username=test%40example.com" in request_body
        assert "password=testpassword" in request_body
        assert "client_id=Zwift_Mobile_Link" in request_body

    @responses.activate
    def test_get_access_token_uses_cached_token(self, auth):
        """Test that valid cached token is returned without API call."""
        # Given - Set up a valid cached token
        auth._access_token = "cached_token"
        auth._access_token_expiration = time.time() + 3600

        # When
        token = auth.get_access_token()

        # Then
        assert token == "cached_token"
        assert len(responses.calls) == 0

    @responses.activate
    def test_get_access_token_refresh_when_expired(self, auth):
        """Test token refresh when access token is expired but refresh token is valid."""
        # Given - Expired access token, valid refresh token
        auth._access_token = "expired_token"
        auth._access_token_expiration = time.time() - 100  # Expired
        auth._refresh_token = "valid_refresh_token"
        auth._refresh_token_expiration = time.time() + 3600  # Still valid

        token_response = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "refresh_expires_in": 86400,
        }
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json=token_response,
            status=200,
        )

        # When
        token = auth.get_access_token()

        # Then
        assert token == "new_access_token"
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        assert "grant_type=refresh_token" in request_body
        assert "refresh_token=valid_refresh_token" in request_body

    @responses.activate
    def test_get_access_token_full_auth_when_refresh_expired(self, auth):
        """Test full auth when both tokens are expired."""
        # Given - Both tokens expired
        auth._access_token = "expired_token"
        auth._access_token_expiration = time.time() - 100
        auth._refresh_token = "expired_refresh_token"
        auth._refresh_token_expiration = time.time() - 100

        token_response = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "refresh_expires_in": 86400,
        }
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json=token_response,
            status=200,
        )

        # When
        token = auth.get_access_token()

        # Then
        assert token == "new_access_token"
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        assert "grant_type=password" in request_body

    @responses.activate
    def test_get_access_token_auth_failure(self, auth):
        """Test handling of authentication failure."""
        # Given
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json={"error": "invalid_grant"},
            status=401,
        )

        # When & Then
        with pytest.raises(ZwiftAuthError, match="Authentication failed"):
            auth.get_access_token()

    @responses.activate
    def test_get_access_token_network_error(self, auth):
        """Test handling of network errors during authentication."""
        # Given
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            body=requests.exceptions.ConnectionError("Connection refused"),
        )

        # When & Then
        with pytest.raises(ZwiftAuthError, match="Failed to connect"):
            auth.get_access_token()

    def test_has_valid_access_token_true(self, auth):
        """Test _has_valid_access_token returns True for valid token."""
        auth._access_token = "valid_token"
        auth._access_token_expiration = time.time() + 3600
        assert auth._has_valid_access_token() is True

    def test_has_valid_access_token_false_expired(self, auth):
        """Test _has_valid_access_token returns False for expired token."""
        auth._access_token = "expired_token"
        auth._access_token_expiration = time.time() - 100
        assert auth._has_valid_access_token() is False

    def test_has_valid_access_token_false_no_token(self, auth):
        """Test _has_valid_access_token returns False when no token."""
        auth._access_token = None
        assert auth._has_valid_access_token() is False
