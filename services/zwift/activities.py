"""Zwift activities module.

Provides access to player activity data.
"""

from typing import Any, Callable, Dict, List

from services.zwift.player_resource import ZwiftPlayerResource


class ZwiftActivities(ZwiftPlayerResource):
    """Provides access to Zwift activity data."""

    def __init__(self, player_id: str, get_access_token: Callable[[], str]):
        """Initialize activities access.

        Args:
            player_id: Player ID or "me" for authenticated user
            get_access_token: Callable that returns a valid access token
        """
        super().__init__(player_id, get_access_token)

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
