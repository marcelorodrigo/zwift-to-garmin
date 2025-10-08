"""Tests for ActivityProcessor."""

import pytest
from unittest.mock import Mock
from services.activity_processor import ActivityProcessor
from services.zwift_service import ZwiftService
from services.fit_file_service import FitFileService
from services.garmin_service import GarminService


class TestActivityProcessor:
    """Test cases for ActivityProcessor."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        zwift_service = Mock(spec=ZwiftService)
        fit_file_service = Mock(spec=FitFileService)
        garmin_service = Mock(spec=GarminService)
        return zwift_service, fit_file_service, garmin_service

    @pytest.fixture
    def activity_processor(self, mock_services):
        """Create an ActivityProcessor instance with mock services."""
        zwift_service, fit_file_service, garmin_service = mock_services
        return ActivityProcessor(zwift_service, fit_file_service, garmin_service)

    def test_init(self, mock_services):
        """Test ActivityProcessor initialization."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        # When
        processor = ActivityProcessor(zwift_service, fit_file_service, garmin_service)

        # Then
        assert processor.zwift_service == zwift_service
        assert processor.fit_file_service == fit_file_service
        assert processor.garmin_service == garmin_service

    def test_process_latest_activity_success(self, activity_processor, mock_services):
        """Test successful activity processing."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        original_file_path = "/tmp/original.fit"
        modified_file_path = "/tmp/modified.fit"
        upload_response = {"upload_id": "12345", "status": "success"}

        zwift_service.download_last_activity.return_value = original_file_path
        fit_file_service.modify_device_info.return_value = modified_file_path
        garmin_service.upload_activity.return_value = upload_response

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is True

        # Verify service calls
        zwift_service.authenticate.assert_called_once()
        zwift_service.download_last_activity.assert_called_once()
        fit_file_service.modify_device_info.assert_called_once_with(original_file_path)
        garmin_service.authenticate.assert_called_once()
        garmin_service.upload_activity.assert_called_once_with(modified_file_path)

        # Verify cleanup
        fit_file_service.cleanup_file.assert_any_call(original_file_path)
        fit_file_service.cleanup_file.assert_any_call(modified_file_path)

    def test_process_latest_activity_no_activities(self, activity_processor, mock_services):
        """Test processing when no activities are found."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        zwift_service.download_last_activity.return_value = None

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify service calls
        zwift_service.authenticate.assert_called_once()
        zwift_service.download_last_activity.assert_called_once()

        # Verify other services are not called
        fit_file_service.modify_device_info.assert_not_called()
        garmin_service.authenticate.assert_not_called()
        garmin_service.upload_activity.assert_not_called()

    def test_process_latest_activity_zwift_auth_failure(self, activity_processor, mock_services):
        """Test processing failure during Zwift authentication."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        zwift_service.authenticate.side_effect = Exception("Zwift auth failed")

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify service calls
        zwift_service.authenticate.assert_called_once()
        zwift_service.download_last_activity.assert_not_called()

    def test_process_latest_activity_download_failure(self, activity_processor, mock_services):
        """Test processing failure during activity download."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        zwift_service.download_last_activity.side_effect = Exception("Download failed")

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify service calls
        zwift_service.authenticate.assert_called_once()
        zwift_service.download_last_activity.assert_called_once()

    def test_process_latest_activity_fit_modification_failure(self, activity_processor, mock_services):
        """Test processing failure during FIT file modification."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        original_file_path = "/tmp/original.fit"
        zwift_service.download_last_activity.return_value = original_file_path
        fit_file_service.modify_device_info.side_effect = Exception("Modification failed")

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify cleanup is still called
        fit_file_service.cleanup_file.assert_called_with(original_file_path)

    def test_process_latest_activity_garmin_auth_failure(self, activity_processor, mock_services):
        """Test processing failure during Garmin authentication."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        original_file_path = "/tmp/original.fit"
        modified_file_path = "/tmp/modified.fit"

        zwift_service.download_last_activity.return_value = original_file_path
        fit_file_service.modify_device_info.return_value = modified_file_path
        garmin_service.authenticate.side_effect = Exception("Garmin auth failed")

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify cleanup is still called
        fit_file_service.cleanup_file.assert_any_call(original_file_path)
        fit_file_service.cleanup_file.assert_any_call(modified_file_path)

    def test_process_latest_activity_upload_failure(self, activity_processor, mock_services):
        """Test processing failure during activity upload."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        original_file_path = "/tmp/original.fit"
        modified_file_path = "/tmp/modified.fit"

        zwift_service.download_last_activity.return_value = original_file_path
        fit_file_service.modify_device_info.return_value = modified_file_path
        garmin_service.upload_activity.side_effect = Exception("Upload failed")

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is False

        # Verify cleanup is still called
        fit_file_service.cleanup_file.assert_any_call(original_file_path)
        fit_file_service.cleanup_file.assert_any_call(modified_file_path)

    def test_process_latest_activity_cleanup_on_success(self, activity_processor, mock_services):
        """Test that cleanup is performed even on successful processing."""
        # Given
        zwift_service, fit_file_service, garmin_service = mock_services

        original_file_path = "/tmp/original.fit"
        modified_file_path = "/tmp/modified.fit"

        zwift_service.download_last_activity.return_value = original_file_path
        fit_file_service.modify_device_info.return_value = modified_file_path
        garmin_service.upload_activity.return_value = {"status": "success"}

        # When
        result = activity_processor.process_latest_activity()

        # Then
        assert result is True

        # Verify cleanup is called
        assert fit_file_service.cleanup_file.call_count == 2
        fit_file_service.cleanup_file.assert_any_call(original_file_path)
        fit_file_service.cleanup_file.assert_any_call(modified_file_path)
