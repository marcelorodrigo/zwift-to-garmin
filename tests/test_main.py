"""Tests for main.py."""

import pytest
from unittest.mock import Mock, patch
import os
from main import main


class TestMain:
    """Test cases for main function."""

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': 'zwift_user',
        'ZWIFT_PASSWORD': 'zwift_pass',
        'GARMIN_USERNAME': 'garmin_user',
        'GARMIN_PASSWORD': 'garmin_pass'
    })
    @patch('main.ActivityProcessor')
    @patch('main.GarminService')
    @patch('main.FitFileService')
    @patch('main.ZwiftService')
    @patch('main.load_dotenv')
    def test_main_success(self, mock_load_dotenv, mock_zwift_service,
                         mock_fit_service, mock_garmin_service, mock_processor):
        """Test successful main execution."""
        # Given
        mock_zwift_instance = Mock()
        mock_fit_instance = Mock()
        mock_garmin_instance = Mock()
        mock_processor_instance = Mock()

        mock_zwift_service.return_value = mock_zwift_instance
        mock_fit_service.return_value = mock_fit_instance
        mock_garmin_service.return_value = mock_garmin_instance
        mock_processor.return_value = mock_processor_instance

        mock_processor_instance.process_latest_activity.return_value = True

        # When
        main()

        # Then
        mock_load_dotenv.assert_called_once()
        mock_zwift_service.assert_called_once_with('zwift_user', 'zwift_pass')
        mock_fit_service.assert_called_once()
        mock_garmin_service.assert_called_once_with('garmin_user', 'garmin_pass')
        mock_processor.assert_called_once_with(
            mock_zwift_instance, mock_fit_instance, mock_garmin_instance
        )
        mock_processor_instance.process_latest_activity.assert_called_once()

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': 'zwift_user',
        'ZWIFT_PASSWORD': 'zwift_pass',
        'GARMIN_USERNAME': 'garmin_user',
        'GARMIN_PASSWORD': 'garmin_pass'
    })
    @patch('main.ActivityProcessor')
    @patch('main.GarminService')
    @patch('main.FitFileService')
    @patch('main.ZwiftService')
    @patch('main.load_dotenv')
    def test_main_processing_failure(self, mock_load_dotenv, mock_zwift_service,
                                   mock_fit_service, mock_garmin_service, mock_processor):
        """Test main execution with processing failure."""
        # Given
        mock_processor_instance = Mock()
        mock_processor.return_value = mock_processor_instance
        mock_processor_instance.process_latest_activity.return_value = False

        # When & Then
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': '',
        'ZWIFT_PASSWORD': 'zwift_pass',
        'GARMIN_USERNAME': 'garmin_user',
        'GARMIN_PASSWORD': 'garmin_pass'
    })
    @patch('main.load_dotenv')
    def test_main_missing_zwift_username(self, mock_load_dotenv):
        """Test main execution with missing Zwift username."""
        # When & Then
        with pytest.raises(ValueError, match="Missing required environment variables"):
            main()

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': 'zwift_user',
        'ZWIFT_PASSWORD': '',
        'GARMIN_USERNAME': 'garmin_user',
        'GARMIN_PASSWORD': 'garmin_pass'
    })
    @patch('main.load_dotenv')
    def test_main_missing_zwift_password(self, mock_load_dotenv):
        """Test main execution with missing Zwift password."""
        # When & Then
        with pytest.raises(ValueError, match="Missing required environment variables"):
            main()

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': 'zwift_user',
        'ZWIFT_PASSWORD': 'zwift_pass',
        'GARMIN_USERNAME': '',
        'GARMIN_PASSWORD': 'garmin_pass'
    })
    @patch('main.load_dotenv')
    def test_main_missing_garmin_username(self, mock_load_dotenv):
        """Test main execution with missing Garmin username."""
        # When & Then
        with pytest.raises(ValueError, match="Missing required environment variables"):
            main()

    @patch.dict(os.environ, {
        'ZWIFT_USERNAME': 'zwift_user',
        'ZWIFT_PASSWORD': 'zwift_pass',
        'GARMIN_USERNAME': 'garmin_user',
        'GARMIN_PASSWORD': ''
    })
    @patch('main.load_dotenv')
    def test_main_missing_garmin_password(self, mock_load_dotenv):
        """Test main execution with missing Garmin password."""
        # When & Then
        with pytest.raises(ValueError, match="Missing required environment variables"):
            main()

    @patch.dict(os.environ, {}, clear=True)
    @patch('main.load_dotenv')
    def test_main_all_env_vars_missing(self, mock_load_dotenv):
        """Test main execution with all environment variables missing."""
        # When & Then
        with pytest.raises(ValueError, match="Missing required environment variables"):
            main()
