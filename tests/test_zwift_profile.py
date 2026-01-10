"""Tests for ZwiftProfile module."""

import pytest
import responses
from services.zwift.profile import ZwiftProfile
from services.zwift.request import ZwiftApiRequest


class TestZwiftProfile:
    """Unit tests for ZwiftProfile (player info/properties)."""

    @pytest.fixture
    def profile_me(self):
        """Profile accessor for 'me'."""
        return ZwiftProfile("me", lambda: "test_token")

    @pytest.fixture
    def profile_explicit(self):
        """Profile accessor for explicit ID."""
        return ZwiftProfile("12345", lambda: "test_token")

    @responses.activate
    def test_profile_me_fetch_profile_data(self, profile_me):
        # Given - resolve me, then fetch profile
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"id": 12345}, status=200,
        )
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345",
            json={"id": 12345, "firstName": "John", "lastName": "Doe", "country": "UK"},
            status=200,
        )
        # When
        player_profile = profile_me.profile
        # Then
        assert player_profile["firstName"] == "John"
        assert player_profile["lastName"] == "Doe"
        assert player_profile["country"] == "UK"
        assert player_profile["id"] == 12345

    @responses.activate
    def test_profile_explicit_id_fetch(self, profile_explicit):
        # Only one GET because no /me lookup
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345",
            json={"id": 12345, "firstName": "Sam", "age": 42},
            status=200,
        )
        player_profile = profile_explicit.profile
        assert player_profile["id"] == 12345
        assert player_profile["firstName"] == "Sam"
        assert player_profile["age"] == 42

    @responses.activate
    def test_me_resolve_caches_id(self, profile_me):
        # me call only once
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"id": 23131}, status=200,
        )
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/23131",
            json={"id": 23131, "foo": "bar"}, status=200,
        )
        _1 = profile_me.profile
        _2 = profile_me.profile
        me_calls = [c for c in responses.calls if c.request.url.endswith("/api/profiles/me")]
        id_calls = [c for c in responses.calls if c.request.url.endswith("/api/profiles/23131")]
        # Only 1 call for /me, but 2 for profile fetch
        assert len(me_calls) == 1
        assert len(id_calls) == 2

    @responses.activate
    def test_profile_error_and_missing_id(self, profile_me):
        # /me resolves with missing id
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={}, status=200,
        )
        with pytest.raises(KeyError):
            _ = profile_me.profile

    @responses.activate
    def test_http_error_propagates(self, profile_me):
        # Server returns HTTP 404
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            status=404,
        )
        with pytest.raises(Exception):  # ZwiftApiError or requests.HTTPError
            _ = profile_me.profile
