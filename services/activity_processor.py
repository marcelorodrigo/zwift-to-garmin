"""Activity processor for orchestrating the Zwift to Garmin workflow."""

import logging
from typing import Optional
from services.zwift_service import ZwiftService
from services.fit_file_service import FitFileService
from services.garmin_service import GarminService


class ActivityProcessor:
    """Main orchestrator for processing activities from Zwift to Garmin."""

    def __init__(self,
                 zwift_service: ZwiftService,
                 fit_file_service: FitFileService,
                 garmin_service: GarminService):
        """Initialize ActivityProcessor with injected services.

        Args:
            zwift_service: Service for Zwift operations
            fit_file_service: Service for FIT file operations
            garmin_service: Service for Garmin operations
        """
        self.zwift_service = zwift_service
        self.fit_file_service = fit_file_service
        self.garmin_service = garmin_service
        self.logger = logging.getLogger(__name__)

    def process_latest_activity(self) -> bool:
        """Process the latest activity from Zwift to Garmin.

        Returns:
            True if successful, False otherwise
        """
        original_file_path: Optional[str] = None
        modified_file_path: Optional[str] = None

        try:
            # Step 1: Authenticate with Zwift and download activity
            self.logger.info("Starting activity processing...")
            self.zwift_service.authenticate()

            original_file_path = self.zwift_service.download_last_activity()
            if not original_file_path:
                self.logger.info("No activities found to process")
                return False

            # Step 2: Modify the FIT file
            modified_file_path = self.fit_file_service.modify_device_info(original_file_path)

            # Step 3: Authenticate with Garmin and upload
            self.garmin_service.authenticate()
            response = self.garmin_service.upload_activity(modified_file_path)

            self.logger.info("Activity processing completed successfully")
            self.logger.debug(f"Upload response: {response}")
            return True

        except Exception as e:
            self.logger.error(f"Activity processing failed: {e}")
            return False

        finally:
            # Clean up temporary files
            if original_file_path:
                self.fit_file_service.cleanup_file(original_file_path)
            if modified_file_path:
                self.fit_file_service.cleanup_file(modified_file_path)
