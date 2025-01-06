# Zwift to Garmin Activity Sync
This project downloads the latest activity from Zwift and uploads it to Garmin Connect.
It also modifies the `.fit` file to set the device manufacturer and type using the Garmin FIT SDK.

## Prerequisites
- Python 3.9+
- `pip3` for managing Python packages
- Zwift and Garmin Connect credentials

## Installation
1. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip3 install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your Zwift and Garmin Connect credentials:
    ```env
    ZWIFT_USERNAME=<your-zwift-username>
    ZWIFT_PASSWORD=<your-zwift-password>
    GARMIN_USERNAME=<your-garmin-username>
    GARMIN_PASSWORD=<your-garmin-password>
    ```

## Usage
Run the main script :smile:

```sh
python main.py
```

## License
This project is licensed under the MIT License.