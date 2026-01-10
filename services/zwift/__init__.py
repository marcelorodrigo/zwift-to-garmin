"""Zwift API Client package.

A modern Python client for the Zwift API that replaces the legacy zwift-client library.

Modules:
    auth: OAuth authentication and token management
    request: Authenticated HTTP requests
    profile: Player profile information
    activities: Player activity data
    client: Main client orchestration
"""

from services.zwift.client import ZwiftClient
from services.zwift.auth import ZwiftAuth, ZwiftAuthError
from services.zwift.request import ZwiftApiError

__all__ = [
    "ZwiftClient",
    "ZwiftAuth",
    "ZwiftAuthError",
    "ZwiftApiError",
]
