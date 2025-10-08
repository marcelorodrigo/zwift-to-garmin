"""Tests for FitFileService."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from services.fit_file_service import FitFileService


class TestFitFileService:
    """Test cases for FitFileService."""

    @pytest.fixture
    def fit_file_service(self):
        """Create a FitFileService instance for testing."""
        return FitFileService()

    @pytest.fixture
    def temp_fit_file(self):
        """Create a temporary FIT file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as temp_file:
            temp_file.write(b'fake fit file content')
            temp_file_path = temp_file.name
        yield temp_file_path
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

    def test_modify_device_info_file_not_found(self, fit_file_service):
        """Test modify_device_info with non-existent file."""
        # When & Then
        with pytest.raises(FileNotFoundError, match="FIT file not found"):
            fit_file_service.modify_device_info("/non/existent/file.fit")

    @patch('services.fit_file_service.FitFile')
    @patch('services.fit_file_service.FitFileBuilder')
    def test_modify_device_info_success(self, mock_builder_class, mock_fit_file_class,
                                       fit_file_service, temp_fit_file):
        """Test successful device info modification."""
        # Given
        mock_content = Mock()
        mock_file_id_message = Mock()
        mock_file_id_message.__class__.__name__ = 'FileIdMessage'
        mock_device_info_message = Mock()
        mock_device_info_message.__class__.__name__ = 'DeviceInfoMessage'

        mock_record1 = Mock()
        mock_record1.message = mock_file_id_message
        mock_record2 = Mock()
        mock_record2.message = mock_device_info_message

        mock_content.records = [mock_record1, mock_record2]
        mock_fit_file_class.from_file.return_value = mock_content

        mock_builder = Mock()
        mock_builder_class.return_value = mock_builder

        mock_built_file = Mock()
        mock_builder.build.return_value = mock_built_file

        # When
        result = fit_file_service.modify_device_info(temp_fit_file)

        # Then
        assert result is not None
        assert 'modified_' in result
        mock_fit_file_class.from_file.assert_called_once_with(temp_fit_file)
        mock_builder.add.assert_called()
        mock_builder.build.assert_called_once()
        mock_built_file.to_file.assert_called_once()

    @patch('services.fit_file_service.FitFile')
    def test_modify_device_info_failure(self, mock_fit_file_class, fit_file_service, temp_fit_file):
        """Test modify_device_info failure."""
        # Given
        mock_fit_file_class.from_file.side_effect = Exception("Processing error")

        # When & Then
        with pytest.raises(RuntimeError, match="Failed to modify FIT file"):
            fit_file_service.modify_device_info(temp_fit_file)

    def test_modify_device_info_with_custom_params(self, fit_file_service, temp_fit_file):
        """Test modify_device_info with custom parameters."""
        # Given
        custom_manufacturer = 123
        custom_product = 456
        custom_version = 1.23

        with patch('services.fit_file_service.FitFile') as mock_fit_file_class, \
             patch('services.fit_file_service.FitFileBuilder') as mock_builder_class:

            mock_content = Mock()
            mock_content.records = []
            mock_fit_file_class.from_file.return_value = mock_content

            mock_builder = Mock()
            mock_builder_class.return_value = mock_builder
            mock_built_file = Mock()
            mock_builder.build.return_value = mock_built_file

            # When
            result = fit_file_service.modify_device_info(
                temp_fit_file,
                manufacturer=custom_manufacturer,
                product=custom_product,
                software_version=custom_version
            )

            # Then
            assert result is not None
            mock_builder_class.assert_called_once_with(auto_define=True, min_string_size=50)

    def test_cleanup_file_exists(self, fit_file_service, temp_fit_file):
        """Test cleanup of existing file."""
        # Given
        assert os.path.exists(temp_fit_file)

        # When
        fit_file_service.cleanup_file(temp_fit_file)

        # Then
        assert not os.path.exists(temp_fit_file)

    def test_cleanup_file_not_exists(self, fit_file_service):
        """Test cleanup of non-existent file."""
        # Given
        non_existent_file = "/tmp/non_existent_file.fit"

        # When (should not raise exception)
        fit_file_service.cleanup_file(non_existent_file)

        # Then - no exception should be raised

    @patch('os.remove')
    def test_cleanup_file_os_error(self, mock_remove, fit_file_service, temp_fit_file):
        """Test cleanup handling OS error."""
        # Given
        mock_remove.side_effect = OSError("Permission denied")

        # When (should not raise exception but log warning)
        fit_file_service.cleanup_file(temp_fit_file)

        # Then
        mock_remove.assert_called_once_with(temp_fit_file)
