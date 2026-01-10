"""Zwift profile module.

Provides access to player profile information.
"""

from typing import Any, Callable, Dict, Optional

from services.zwift.request import ZwiftApiRequest


class ZwiftProfile:
    """Provides access to Zwift player profile data."""

    def __init__(self, player_id: str, get_access_token: Callable[[], str]):
        """Initialize profile access.

        Args:
            player_id: Player ID or "me" for authenticated user
            get_access_token: Callable that returns a valid access token
        """
        self._player_id = player_id
        self._request = ZwiftApiRequest(get_access_token)
        self._resolved_player_id: Optional[str] = None

    def _get_player_id(self) -> str:
        """Get the resolved player ID, fetching from API if needed.

        Returns:
            The numeric player ID
        """
        if self._resolved_player_id:
            return self._resolved_player_id

        if self._player_id != "me":
            self._resolved_player_id = self._player_id
            return self._player_id

        # Resolve "me" to actual player ID
        profile_data = self._request.get_json("/api/profiles/me")
        self._resolved_player_id = str(profile_data["id"])
        return self._resolved_player_id

    @property
    def profile(self) -> Dict[str, Any]:
        """Get the player's profile data.

        Returns:
            Profile data dictionary
        """
        return self._request.get_json(f"/api/profiles/{self._get_player_id()}")
