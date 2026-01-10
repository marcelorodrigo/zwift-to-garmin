"""Integration tests for the ZwiftClient orchestrator."""

import time
import pytest
import responses
from services.zwift import ZwiftClient, ZwiftAuth


class TestZwiftClientIntegration:
    """Integration tests for ZwiftClient."""

    def test_client_initialization(self):
        """Test client initializes with credentials."""
        # When
        client = ZwiftClient("user@test.com", "password123")

        # Then
        assert client._auth.username == "user@test.com"
        assert client._auth.password == "password123"

    def test_get_profile_returns_activities_instance(self):
        """Test get_profile returns a ZwiftActivities instance."""
        # Given
        client = ZwiftClient("user@test.com", "password123")

        # When
        profile = client.get_profile()

        # Then - The interface uses "profile" but returns activities accessor
        assert hasattr(profile, "get_activities")
        assert profile._player_id == "me"

    def test_get_profile_with_player_id(self):
        """Test get_profile with specific player ID."""
        # Given
        client = ZwiftClient("user@test.com", "password123")

        # When
        profile = client.get_profile("12345")

        # Then
        assert hasattr(profile, "get_activities")
        assert profile._player_id == "12345"

    @responses.activate
    def test_full_workflow(self):
        """Test complete workflow: auth -> profile -> activities."""
        # Given
        # Auth response
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "refresh_expires_in": 86400,
            },
            status=200,
        )
        # Profile resolution
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/me",
            json={"id": 12345},
            status=200,
        )
        # Activities
        activities = [
            {
                "id": "activity123",
                "fitFileBucket": "zwift-activity-files",
                "fitFileKey": "user/12345/activity123.fit",
            }
        ]
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/12345/activities?start=0&limit=10",
            json=activities,
            status=200,
        )

        # When
        client = ZwiftClient("user@test.com", "password123")
        profile = client.get_profile()
        result = profile.get_activities()

        # Then
        assert len(result) == 1
        assert result[0]["id"] == "activity123"
        assert result[0]["fitFileBucket"] == "zwift-activity-files"

    @responses.activate
    def test_token_refresh_during_activity_fetch(self):
        """Test that token refresh works transparently during API calls."""
        # Given - Use explicit player ID to avoid extra API call for resolution
        client = ZwiftClient("user@test.com", "password123")

        # First auth
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json={
                "access_token": "initial_token",
                "refresh_token": "refresh_token",
                "expires_in": 3600,
                "refresh_expires_in": 86400,
            },
            status=200,
        )

        # First activities call
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/12345/activities?start=0&limit=10",
            json=[{"id": "act1"}],
            status=200,
        )

        # Use explicit player ID to skip profile resolution
        profile = client.get_profile("12345")
        profile.get_activities()

        # Simulate token expiry by manipulating internal state
        client._auth._access_token_expiration = time.time() - 100

        # Token refresh
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json={
                "access_token": "refreshed_token",
                "refresh_token": "new_refresh_token",
                "expires_in": 3600,
                "refresh_expires_in": 86400,
            },
            status=200,
        )

        # Second activities call with refreshed token
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/12345/activities?start=0&limit=10",
            json=[{"id": "act2"}],
            status=200,
        )

        # When - Make another call after token expired
        result = profile.get_activities()

        # Then
        assert len(result) == 1
        assert result[0]["id"] == "act2"
        # Verify refresh was called (initial auth + refresh)
        auth_calls = [c for c in responses.calls if c.request.url and "auth" in c.request.url]
        assert len(auth_calls) == 2

    @responses.activate
    def test_multiple_profiles_same_client(self):
        """Test creating multiple profile accessors from same client."""
        # Given
        client = ZwiftClient("user@test.com", "password123")

        # Auth setup
        responses.add(
            responses.POST,
            ZwiftAuth.AUTH_URL,
            json={
                "access_token": "test_token",
                "refresh_token": "test_refresh",
                "expires_in": 3600,
                "refresh_expires_in": 86400,
            },
            status=200,
        )

        # Profile 1
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/111/activities?start=0&limit=10",
            json=[{"id": "act_111"}],
            status=200,
        )

        # Profile 2
        responses.add(
            responses.GET,
            "https://us-or-rly101.zwift.com/api/profiles/222/activities?start=0&limit=10",
            json=[{"id": "act_222"}],
            status=200,
        )

        # When - Create profiles for different users
        profile1 = client.get_profile("111")
        profile2 = client.get_profile("222")

        result1 = profile1.get_activities()
        result2 = profile2.get_activities()

        # Then
        assert result1[0]["id"] == "act_111"
        assert result2[0]["id"] == "act_222"
