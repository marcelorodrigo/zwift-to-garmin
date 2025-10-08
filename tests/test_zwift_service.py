"""Tests for ZwiftService."""

import pytest
import responses
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from services.zwift_service import ZwiftService


class TestZwiftService:
    """Test cases for ZwiftService."""

    @pytest.fixture
    def zwift_service(self):
        """Create a ZwiftService instance for testing."""
        return ZwiftService("test_user", "test_pass")

    @patch('services.zwift_service.ZwiftClient')
    def test_authenticate_success(self, mock_client_class, zwift_service):
        """Test successful authentication with Zwift."""
        # Given
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # When
        zwift_service.authenticate()

        # Then
        mock_client_class.assert_called_once_with("test_user", "test_pass")
        assert zwift_service.client == mock_client

    def test_download_last_activity_not_authenticated(self, zwift_service):
        """Test download fails when not authenticated."""
        # When & Then
        with pytest.raises(RuntimeError, match="Must authenticate before downloading activities"):
            zwift_service.download_last_activity()

    @patch('services.zwift_service.ZwiftClient')
    @responses.activate
    def test_download_last_activity_no_activities(self, mock_client_class, zwift_service):
        """Test download when no activities are found."""
        # Given
        mock_client = Mock()
        mock_profile = Mock()
        mock_profile.get_activities.return_value = []
        mock_client.get_profile.return_value = mock_profile
        mock_client_class.return_value = mock_client

        zwift_service.authenticate()

        # When
        result = zwift_service.download_last_activity()

        # Then
        assert result is None

    @patch('services.zwift_service.ZwiftClient')
    @responses.activate
    def test_download_last_activity_success(self, mock_client_class, zwift_service):
        """Test successful activity download."""
        # Given
        mock_client = Mock()
        mock_profile = Mock()

        # Mock activity data
        activity_data = {
            'id': '12345',
            'fitFileBucket': 'test-bucket',
            'fitFileKey': 'test-key.fit'
        }
        mock_profile.get_activities.return_value = [activity_data]
        mock_client.get_profile.return_value = mock_profile
        mock_client_class.return_value = mock_client

        # Mock the HTTP response for file download
        fit_file_content = b'fake fit file content'
        responses.add(
            responses.GET,
            'https://test-bucket.s3.amazonaws.com/test-key.fit',
            body=fit_file_content,
            status=200
        )

        zwift_service.authenticate()

        # When
        result = zwift_service.download_last_activity()

        # Then
        assert result is not None
        assert os.path.exists(result)
        assert 'zwift_activity_12345.fit' in result

        # Verify file content
        with open(result, 'rb') as f:
            assert f.read() == fit_file_content

        # Cleanup
        os.remove(result)

    @patch('services.zwift_service.ZwiftClient')
    @responses.activate
    def test_download_last_activity_http_error(self, mock_client_class, zwift_service):
        """Test download failure due to HTTP error."""
        # Given
        mock_client = Mock()
        mock_profile = Mock()

        activity_data = {
            'id': '12345',
            'fitFileBucket': 'test-bucket',
            'fitFileKey': 'test-key.fit'
        }
        mock_profile.get_activities.return_value = [activity_data]
        mock_client.get_profile.return_value = mock_profile
        mock_client_class.return_value = mock_client

        # Mock HTTP error
        responses.add(
            responses.GET,
            'https://test-bucket.s3.amazonaws.com/test-key.fit',
            status=404
        )

        zwift_service.authenticate()

        # When & Then
        with pytest.raises(RuntimeError, match="Failed to download activity"):
            zwift_service.download_last_activity()
