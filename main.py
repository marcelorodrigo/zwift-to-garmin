import os
import tempfile
import requests
import logging
from zwift import Client as ZwiftClient
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectTooManyRequestsError,
    GarminConnectConnectionError
)
from dotenv import load_dotenv
from fit_tool.fit_file import FitFile
from fit_tool.profile.messages.device_info_message import DeviceInfoMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.profile_type import Manufacturer, GarminProduct
from fit_tool.fit_file_builder import FitFileBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

ZWIFT_USERNAME = os.getenv("ZWIFT_USERNAME")
ZWIFT_PASSWORD = os.getenv("ZWIFT_PASSWORD")
GARMIN_USERNAME = os.getenv("GARMIN_USERNAME")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

def download_last_activity(zwift_client):
    """Downloads the last activity's .fit file from Zwift."""
    profile = zwift_client.get_profile()
    activities = profile.get_activities()

    if not activities:
        print("No activities found on Zwift.")
        return None

    last_activity = activities[0]  # The most recent activity
    activity_id = last_activity['id']
    logging.info(f"Downloading activity {activity_id}...")

    link = "https://" + last_activity["fitFileBucket"] + ".s3.amazonaws.com/" + last_activity["fitFileKey"]
    print(f"Download link: {link}")
    res = requests.get(link)


    # Save the .fit file to a temporary location
    temp_dir = tempfile.gettempdir()
    fit_file_path = os.path.join(temp_dir, f"zwift_activity_{activity_id}.fit")
    with open(fit_file_path, "wb") as file:
        file.write(res.content)

    print(f"Activity {activity_id} downloaded to {fit_file_path}")
    return fit_file_path

def upload_to_garmin(garmin_client, fit_file_path):
    """Uploads a .fit file to Garmin Connect."""
    print(f"Uploading {fit_file_path} to Garmin Connect...")
    response = garmin_client.upload_activity(fit_file_path)
    print("Upload response:", response)

def modify_fit_file(fit_file_path):
    """Modifies the device manufacturer and type in a .fit file using Garmin FIT SDK."""
    print(f"Modifying .fit file: {fit_file_path}")

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
    fit_file = builder.build()

    # Encode the modified FIT file
    temp_dir = tempfile.gettempdir()
    modified_fit_file_path = os.path.join(temp_dir, "modified_" + os.path.basename(fit_file_path))
    fit_file.to_file(modified_fit_file_path)

    print(f"Modified .fit file saved to {modified_fit_file_path}")
    return modified_fit_file_path


def main():
    # Authenticate with Zwift
    zwift_client = ZwiftClient(ZWIFT_USERNAME, ZWIFT_PASSWORD)

    # Download the last activity from Zwift
    fit_file_path = download_last_activity(zwift_client)

    if fit_file_path:
        new_file_path = modify_fit_file(fit_file_path)
        # Upload the activity to Garmin Connect
        # Authenticate with Garmin Connect
        garmin_client = Garmin(GARMIN_USERNAME, GARMIN_PASSWORD)
        print("Logging in to Garmin Connect...")
        try:
            garmin_client.login()
        except GarminConnectAuthenticationError:
            print("Authentication error. Check your credentials.")
        except GarminConnectTooManyRequestsError:
            print("Too many requests. Try again later.")
        except GarminConnectConnectionError:
            print("Connection error. Check your internet connection.")
        except Exception as e:
            print(f"Failed to login to Garmin Connect: {e}")
            return
        
        #try:
        upload_to_garmin(garmin_client, new_file_path)
        #except Exception as e:
        #    print(f"Failed to upload activity to Garmin Connect: {e}")
        

        # Clean up the temporary .fit file
        os.remove(fit_file_path)

if __name__ == "__main__":
    main()