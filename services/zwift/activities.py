"""Zwift activities module.

Provides access to player activity data.
"""

from typing import Any, Callable, Dict, List, Optional

from services.zwift.request import ZwiftApiRequest


class ZwiftActivities:
    """Provides access to Zwift activity data."""

    def __init__(self, player_id: str, get_access_token: Callable[[], str]):
        """Initialize activities access.

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

    def get_activities(self, start: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the player's activities.

        Args:
            start: Starting index for pagination
            limit: Maximum number of activities to return

        Returns:
            List of activity dictionaries
        """
        endpoint = f"/api/profiles/{self._get_player_id()}/activities?start={start}&limit={limit}"
        return self._request.get_json(endpoint)
