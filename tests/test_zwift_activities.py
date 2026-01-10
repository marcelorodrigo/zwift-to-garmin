"""Tests for Zwift activities module."""

import pytest
import responses

from services.zwift.activities import ZwiftActivities
from services.zwift.request import ZwiftApiRequest


class TestZwiftActivities:
    """Tests for ZwiftActivities class."""

    @pytest.fixture
    def activities(self):
        """Create a ZwiftActivities instance for testing."""
        return ZwiftActivities("me", lambda: "test_token")

    @responses.activate
    def test_get_activities(self, activities):
        """Test getting activities list."""
        # Given - First call resolves player ID
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"id": 12345},
            status=200,
        )
        # Second call gets activities
        activity_list = [
            {"id": "activity1", "fitFileBucket": "bucket1", "fitFileKey": "key1.fit"},
            {"id": "activity2", "fitFileBucket": "bucket2", "fitFileKey": "key2.fit"},
        ]
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345/activities?start=0&limit=10",
            json=activity_list,
            status=200,
        )

        # When
        result = activities.get_activities()

        # Then
        assert len(result) == 2
        assert result[0]["id"] == "activity1"
        assert result[1]["id"] == "activity2"

    @responses.activate
    def test_get_activities_with_pagination(self, activities):
        """Test getting activities with custom pagination."""
        # Given
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"id": 12345},
            status=200,
        )
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345/activities?start=10&limit=5",
            json=[{"id": "activity11"}],
            status=200,
        )

        # When
        result = activities.get_activities(start=10, limit=5)

        # Then
        assert len(result) == 1

    @responses.activate
    def test_player_id_resolution_cached(self, activities):
        """Test that player ID is resolved only once."""
        # Given
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/me",
            json={"id": 12345},
            status=200,
        )
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345/activities?start=0&limit=10",
            json=[],
            status=200,
        )
        responses.add(
            responses.GET,
            f"{ZwiftApiRequest.BASE_URL}/api/profiles/12345/activities?start=0&limit=10",
            json=[],
            status=200,
        )

        # When - Call get_activities twice
        activities.get_activities()
        activities.get_activities()

        # Then - Only one call to resolve player ID
        profile_calls = [c for c in responses.calls if c.request.url and "/api/profiles/me" in c.request.url]
        assert len(profile_calls) == 1

    def test_explicit_player_id_no_resolution(self):
        """Test that explicit player ID doesn't require resolution."""
        # Given
        activities = ZwiftActivities("99999", lambda: "test_token")

        # When
        player_id = activities._get_player_id()

        # Then
        assert player_id == "99999"
