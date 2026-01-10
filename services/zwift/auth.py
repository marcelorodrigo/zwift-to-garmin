"""Zwift OAuth authentication module.

Handles token management and authentication with Zwift's OAuth server.
"""

import time
import logging
from typing import Optional, Dict, Any

import requests


class ZwiftAuthError(Exception):
    """Raised when authentication with Zwift fails."""

    pass


class ZwiftAuth:
    """Manages OAuth authentication and token lifecycle with Zwift.

    Automatically handles token refresh when tokens expire.
    """

    AUTH_URL = "https://secure.zwift.com/auth/realms/zwift/tokens/access/codes"
    CLIENT_ID = "Zwift_Mobile_Link"
    # Buffer time (seconds) before token expiration to trigger refresh
    TOKEN_EXPIRY_BUFFER = 30

    def __init__(self, username: str, password: str):
        """Initialize authentication with Zwift credentials.

        Args:
            username: Zwift account username/email
            password: Zwift account password
        """
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)

        # Token data
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._access_token_expiration: float = 0
        self._refresh_token_expiration: float = 0

    def _fetch_token(self, use_refresh: bool = False) -> Dict[str, Any]:
        """Fetch a new token from Zwift's auth server.

        Args:
            use_refresh: If True, use refresh token grant; otherwise use password grant

        Returns:
            Token response data from the API

        Raises:
            ZwiftAuthError: If authentication fails
        """
        if use_refresh and self._refresh_token:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": self.CLIENT_ID,
            }
        else:
            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.CLIENT_ID,
            }

        try:
            response = requests.post(self.AUTH_URL, data=data, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_msg = f"Authentication failed: {e}"
            if e.response is not None and e.response.text:
                error_msg += f" - {e.response.text}"
            raise ZwiftAuthError(error_msg) from e
        except requests.exceptions.RequestException as e:
            raise ZwiftAuthError(f"Failed to connect to Zwift auth server: {e}") from e

    def _update_tokens(self, token_data: Dict[str, Any]) -> None:
        """Update stored tokens from API response.

        Args:
            token_data: Token response from the auth API
        """
        now = time.time()
        self._access_token = token_data.get("access_token")
        self._refresh_token = token_data.get("refresh_token")

        expires_in = token_data.get("expires_in", 3600)
        refresh_expires_in = token_data.get("refresh_expires_in", 86400)

        self._access_token_expiration = now + expires_in - self.TOKEN_EXPIRY_BUFFER
        self._refresh_token_expiration = now + refresh_expires_in - self.TOKEN_EXPIRY_BUFFER

    def _has_valid_access_token(self) -> bool:
        """Check if the current access token is still valid."""
        return bool(self._access_token and time.time() < self._access_token_expiration)

    def _has_valid_refresh_token(self) -> bool:
        """Check if the current refresh token is still valid."""
        return bool(self._refresh_token and time.time() < self._refresh_token_expiration)

    def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary.

        Returns:
            A valid access token string

        Raises:
            ZwiftAuthError: If unable to obtain a valid token
        """
        if self._has_valid_access_token() and self._access_token:
            return self._access_token

        # Try to refresh, or do full auth if refresh token is expired
        use_refresh = self._has_valid_refresh_token()
        self.logger.debug(
            "Fetching new token via %s",
            "refresh" if use_refresh else "password grant"
        )

        token_data = self._fetch_token(use_refresh=use_refresh)
        self._update_tokens(token_data)

        if not self._access_token:
            raise ZwiftAuthError("Failed to obtain access token from response")

        return self._access_token
