"""Tests for GarminService."""

import pytest
from unittest.mock import Mock, patch
from garminconnect import (
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
    GarminConnectConnectionError
)
from services.garmin_service import GarminService


class TestGarminService:
    """Test cases for GarminService."""

    @pytest.fixture
    def garmin_service(self):
        """Create a GarminService instance for testing."""
        with patch('services.garmin_service.Garmin') as mock_garmin_class:
            mock_client = Mock()
            mock_garmin_class.return_value = mock_client
            service = GarminService("test_user", "test_pass")
            service.client = mock_client
            return service

    def test_init(self):
        """Test GarminService initialization."""
        with patch('services.garmin_service.Garmin') as mock_garmin_class:
            mock_client = Mock()
            mock_garmin_class.return_value = mock_client

            # When
            service = GarminService("test_user", "test_pass")

            # Then
            assert service.username == "test_user"
            assert service.password == "test_pass"
            assert service.client == mock_client
            assert not service._authenticated
            mock_garmin_class.assert_called_once_with("test_user", "test_pass")

    def test_authenticate_success(self, garmin_service):
        """Test successful authentication."""
        # Given
        garmin_service.client.login.return_value = None

        # When
        garmin_service.authenticate()

        # Then
        garmin_service.client.login.assert_called_once()
        assert garmin_service._authenticated is True

    def test_authenticate_auth_error(self, garmin_service):
        """Test authentication failure with invalid credentials."""
        # Given
        garmin_service.client.login.side_effect = GarminConnectAuthenticationError("Invalid credentials")

        # When & Then
        with pytest.raises(GarminConnectAuthenticationError):
            garmin_service.authenticate()
        assert garmin_service._authenticated is False

    def test_authenticate_rate_limit_error(self, garmin_service):
        """Test authentication failure due to rate limiting."""
        # Given
        garmin_service.client.login.side_effect = GarminConnectTooManyRequestsError("Rate limit exceeded")

        # When & Then
        with pytest.raises(GarminConnectTooManyRequestsError):
            garmin_service.authenticate()
        assert garmin_service._authenticated is False

    def test_authenticate_connection_error(self, garmin_service):
        """Test authentication failure due to connection issues."""
        # Given
        garmin_service.client.login.side_effect = GarminConnectConnectionError("Connection failed")

        # When & Then
        with pytest.raises(GarminConnectConnectionError):
            garmin_service.authenticate()
        assert garmin_service._authenticated is False

    def test_authenticate_generic_error(self, garmin_service):
        """Test authentication failure with generic error."""
        # Given
        garmin_service.client.login.side_effect = Exception("Unexpected error")

        # When & Then
        with pytest.raises(RuntimeError, match="Authentication failed"):
            garmin_service.authenticate()
        assert garmin_service._authenticated is False

    def test_upload_activity_not_authenticated(self, garmin_service):
        """Test upload fails when not authenticated."""
        # When & Then
        with pytest.raises(RuntimeError, match="Must authenticate before uploading activities"):
            garmin_service.upload_activity("/path/to/file.fit")

    def test_upload_activity_success(self, garmin_service):
        """Test successful activity upload."""
        # Given
        garmin_service._authenticated = True
        expected_response = {"upload_id": "12345", "status": "success"}
        garmin_service.client.upload_activity.return_value = expected_response

        # When
        result = garmin_service.upload_activity("/path/to/file.fit")

        # Then
        assert result == expected_response
        garmin_service.client.upload_activity.assert_called_once_with("/path/to/file.fit")

    def test_upload_activity_failure(self, garmin_service):
        """Test upload failure."""
        # Given
        garmin_service._authenticated = True
        garmin_service.client.upload_activity.side_effect = Exception("Upload failed")

        # When & Then
        with pytest.raises(RuntimeError, match="Upload failed"):
            garmin_service.upload_activity("/path/to/file.fit")

    def test_is_authenticated_true(self, garmin_service):
        """Test is_authenticated returns True when authenticated."""
        # Given
        garmin_service._authenticated = True

        # When & Then
        assert garmin_service.is_authenticated() is True

    def test_is_authenticated_false(self, garmin_service):
        """Test is_authenticated returns False when not authenticated."""
        # Given
        garmin_service._authenticated = False

        # When & Then
        assert garmin_service.is_authenticated() is False
