"""Zwift API request module.

Handles authenticated HTTP requests to Zwift's API endpoints.
"""

import logging
from typing import Any, Callable, Dict

import requests


class ZwiftApiError(Exception):
    """Raised when a Zwift API request fails."""

    pass


class ZwiftApiRequest:
    """Handles authenticated API requests to Zwift."""

    BASE_URL = "https://us-or-rly101.zwift.com"
    DEFAULT_HEADERS = {
        "User-Agent": "Zwift/115 CFNetwork/758.0.2 Darwin/15.0.0",
    }
    REQUEST_TIMEOUT = 30

    def __init__(self, get_access_token: Callable[[], str]):
        """Initialize with a token provider function.

        Args:
            get_access_token: Callable that returns a valid access token
        """
        self._get_access_token = get_access_token
        self.logger = logging.getLogger(__name__)

    def _get_headers(self, accept_type: str = "application/json") -> Dict[str, str]:
        """Build request headers with authorization.

        Args:
            accept_type: MIME type for Accept header

        Returns:
            Headers dictionary
        """
        headers = {
            "Accept": accept_type,
            "Authorization": f"Bearer {self._get_access_token()}",
        }
        headers.update(self.DEFAULT_HEADERS)
        return headers

    def get_json(self, endpoint: str) -> Any:
        """Make a GET request and return JSON response.

        Args:
            endpoint: API endpoint path (e.g., "/api/profiles/me")

        Returns:
            Parsed JSON response

        Raises:
            ZwiftApiError: If the request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers("application/json")

        try:
            response = requests.get(url, headers=headers, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            try:
                return response.json()
            except ValueError as decode_err:
                snippet = response.text[:200].strip()  # Limit body preview
                raise ZwiftApiError(f"API response not JSON-decodable (status={response.status_code}): {snippet}") from decode_err
        except requests.exceptions.HTTPError as e:
            raise ZwiftApiError(f"API request failed: {e.response.status_code} - {e.response.reason}") from e
        except requests.exceptions.RequestException as e:
            raise ZwiftApiError(f"Failed to connect to Zwift API: {e}") from e
