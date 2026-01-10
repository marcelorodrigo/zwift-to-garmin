"""Zwift profile module.

Provides access to player profile information.
"""

from typing import Any, Callable, Dict

from services.zwift.player_resource import ZwiftPlayerResource


class ZwiftProfile(ZwiftPlayerResource):
    """Provides access to Zwift player profile data."""

    def __init__(self, player_id: str, get_access_token: Callable[[], str]):
        """Initialize profile access.

        Args:
            player_id: Player ID or "me" for authenticated user
            get_access_token: Callable that returns a valid access token
        """
        super().__init__(player_id, get_access_token)

    @property
    def profile(self) -> Dict[str, Any]:
        """Get the player's profile data.

        Returns:
            Profile data dictionary
        """
        return self._request.get_json(f"/api/profiles/{self._get_player_id()}")
