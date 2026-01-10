"""Zwift API Client.

Main client module that orchestrates authentication and API access.
This is a modern, drop-in replacement for the legacy zwift-client library.
"""

from services.zwift.auth import ZwiftAuth
from services.zwift.activities import ZwiftActivities


class ZwiftClient:
    """Main client for interacting with Zwift's API.

    This is a drop-in replacement for the zwift-client library's Client class,
    providing only the functionality needed for activity retrieval.

    Example:
        client = ZwiftClient("user@example.com", "password")
        profile = client.get_profile()
        activities = profile.get_activities()
    """

    def __init__(self, username: str, password: str):
        """Initialize the Zwift client with credentials.

        Args:
            username: Zwift account username/email
            password: Zwift account password
        """
        self._auth = ZwiftAuth(username, password)

    def get_profile(self, player_id: str = "me") -> ZwiftActivities:
        """Get an activities accessor for the specified player.

        Args:
            player_id: Player ID or "me" for authenticated user (default)

        Returns:
            ZwiftActivities instance for accessing activity data
        """
        return ZwiftActivities(player_id, self._auth.get_access_token)
