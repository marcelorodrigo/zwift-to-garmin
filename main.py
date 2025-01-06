import logging
import os
import sys
import tempfile

import requests
from dotenv import load_dotenv
from fit_tool.fit_file import FitFile
from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.profile_type import Manufacturer, GarminProduct
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
    GarminConnectConnectionError
)
from zwift import Client as ZwiftClient

class CustomFormatter(logging.Formatter):
    """Custom logging formatter to add colors and remove timestamp."""

    # Define log colors
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m',# Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[95m'# Magenta
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        log_message = f"{log_color}{record.getMessage()}{self.RESET}"
        return log_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Remove all handlers associated with the root logger
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Set custom formatter
handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)

# Load environment variables from .env file
load_dotenv()

ZWIFT_USERNAME = os.getenv("ZWIFT_USERNAME")
ZWIFT_PASSWORD = os.getenv("ZWIFT_PASSWORD")
GARMIN_USERNAME = os.getenv("GARMIN_USERNAME")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")


def create_env_file_if_not_exists():
    """Creates a .env file from the .env_sample file if it doesn't exist."""
    env_file = '.env'
    if not os.path.exists(env_file):
        with open('.env_sample', 'r') as sample_file:
            content = sample_file.read()
        with open(env_file, 'w') as new_env_file:
            new_env_file.write(content)
        logger.info("You missed the setup. Please update .env with your credentials.")
        sys.exit(1)


def download_last_activity(zwift_client):
    """Downloads the last activity's .fit file from Zwift."""
    try:
        profile = zwift_client.get_profile()
        activities = profile.get_activities()

        if not activities:
            logger.info("No activities found on Zwift.")
            return None

        last_activity = activities[0]  # The most recent activity
        activity_id = last_activity['id']
        logging.info(f"Downloading activity {activity_id}...")

        link = "https://" + last_activity["fitFileBucket"] + ".s3.amazonaws.com/" + last_activity["fitFileKey"]
        logger.info(f"Downloading {link}")
        res = requests.get(link)

        # Save the .fit file to a temporary location
        temp_dir = tempfile.gettempdir()
        fit_file_path = os.path.join(temp_dir, f"zwift_activity_{activity_id}.fit")
        with open(fit_file_path, "wb") as file:
            file.write(res.content)

        logger.info(f"Activity {activity_id} downloaded to {fit_file_path}")
        return fit_file_path
    except Exception as e:
        logger.error(f"An error occurred while downloading the last activity from Zwift: {e}")
        return None


def upload_to_garmin(garmin_client, fit_file_path):
    """Uploads a .fit file to Garmin Connect."""
    logger.info(f"Uploading {fit_file_path} to Garmin Connect")
    response = garmin_client.upload_activity(fit_file_path)
    if response.status_code == 202:
        logger.info("Ride On! Garmin Upload successful.")
    else:
        logger.info("Garmin Upload failed. Response:", response)

def modify_fit_file(fit_file_path):
    """Modifies the device manufacturer and type in a .fit file using Garmin FIT SDK."""
    logger.info(f"Modifying {fit_file_path} to appear as recorded in a Garmin Edge 530")

    content = FitFile.from_file(fit_file_path)

    # Set auto_define to true, so that the builder creates the required Definition Messages for us.
    builder = FitFileBuilder(auto_define=True, min_string_size=50)

    for record in content.records:
        message = record.message
        if isinstance(message, FileIdMessage):
            message.manufacturer = Manufacturer.GARMIN.value
            message.product = GarminProduct.EDGE_530.value
        elif isinstance(message, DeviceInfoMessage):
            message.manufacturer = Manufacturer.GARMIN.value
            message.product = GarminProduct.EDGE_530.value
            message.software_version = 9.75
        builder.add(message)

    # Finally build the FIT file object and write it to a file
    logger.info("Building the modified FIT file")
    fit_file = builder.build()

    # Encode the modified FIT file
    temp_dir = tempfile.gettempdir()
    modified_fit_file_path = os.path.join(temp_dir, "modified_" + os.path.basename(fit_file_path))
    logger.info(f"Saving the modified .fit file to {modified_fit_file_path}")
    fit_file.to_file(modified_fit_file_path)

    return modified_fit_file_path


def main():
    create_env_file_if_not_exists()

    if ZWIFT_USERNAME == 'your_zwift_username' or ZWIFT_PASSWORD == 'your_zwift_password':
        logger.error("Hold the line! Please update your credentials in the .env file")
        sys.exit(1)


    # Authenticate with Zwift
    zwift_client = ZwiftClient(ZWIFT_USERNAME, ZWIFT_PASSWORD)

    # Download the last activity from Zwift
    fit_file_path = download_last_activity(zwift_client)

    if fit_file_path:
        new_file_path = modify_fit_file(fit_file_path)
        # Upload the activity to Garmin Connect
        # Authenticate with Garmin Connect
        garmin_client = Garmin(GARMIN_USERNAME, GARMIN_PASSWORD)
        logger.info(f"Logging in to Garmin Connect with user {GARMIN_USERNAME}...")
        try:
            garmin_client.login()
        except GarminConnectAuthenticationError:
            logger.info("Garmin authentication error. Check your credentials.")
        except GarminConnectTooManyRequestsError:
            logger.info("Garmin said too many requests. Try again later.")
        except GarminConnectConnectionError:
            logger.info("Garmin Connection error. Check your credentials or internet connection.")
        except Exception as e:
            logger.info(f"Failed to login to Garmin Connect: {e}")
            return

        # try:
        upload_to_garmin(garmin_client, new_file_path)
        # except Exception as e:
        #    logger.info(f"Failed to upload activity to Garmin Connect: {e}")

        # Clean up the temporary .fit file
        os.remove(fit_file_path)


if __name__ == "__main__":
    main()
