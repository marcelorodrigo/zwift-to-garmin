"""Base class for Zwift player resources.

Provides shared player ID resolution logic for accessing player-specific endpoints.
"""

from typing import Callable, Optional

from services.zwift.request import ZwiftApiRequest


class ZwiftPlayerResource:
    """Base class for Zwift resources that require player ID resolution.

    Handles the logic of resolving "me" to an actual numeric player ID,
    with caching to avoid repeated API calls.
    """

    def __init__(self, player_id: str, get_access_token: Callable[[], str]):
        """Initialize player resource.

        Args:
            player_id: Player ID or "me" for authenticated user
            get_access_token: Callable that returns a valid access token
        """
        self._player_id = player_id
        self._request = ZwiftApiRequest(get_access_token)
        self._resolved_player_id: Optional[str] = None

    def _get_player_id(self) -> str:
        """Get the resolved player ID, fetching from API if needed.

        If initialized with "me", makes an API call to resolve to the actual
        numeric player ID. Otherwise, returns the provided ID directly.
        Result is cached for subsequent calls.

        Returns:
            The numeric player ID as a string
        """
        if self._resolved_player_id:
            return self._resolved_player_id

        if self._player_id != "me":
            self._resolved_player_id = self._player_id
            return self._player_id

        # Resolve "me" to actual player ID via API
        profile_data = self._request.get_json("/api/profiles/me")
        self._resolved_player_id = str(profile_data["id"])
        return self._resolved_player_id
