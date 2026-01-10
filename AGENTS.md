# AGENTS.md

## Project: Zwift to Garmin Activity Transfer

This codebase is organized for robust, testable, and modular transfer of cycling activity data from Zwift to Garmin Connect. This document provides AI coding agents with the quick reference and patterns necessary for productive, context-aware contribution.

---

## 🏗️ Architecture Overview

- **Service-Oriented (Dependency Injection)**
  - Major workflows are orchestrated in `services/activity_processor.py`.
  - Each domain (Zwift, FIT file mangling, Garmin, workflow) has its own service under `services/`.
  - The modular `services/zwift/` implements a full REST client (auth, activities, request, etc); no third-party zwift-client library is used.

- **Key Flow**
  1. `main.py` loads `.env` for credentials, initializes services.
  2. `ActivityProcessor`:
      - Authenticates with Zwift (`ZwiftService`)
      - Downloads activity + modifies FIT (`FitFileService`)
      - Authenticates + uploads to Garmin (`GarminService`)
      - Cleans up files on success/failure

- **Testing**
  - Tests for each service live in `tests/`; all core APIs are tested individually and via integration.
  - Run: `pytest -v` (see also README for full test/coverage commands).

---

## Key Files and Responsibilities

- `services/zwift/`: Modular Zwift REST API client (auth, requests, profile, activities, etc)
- `services/zwift_service.py`: Loads ZwiftClient and handles download of latest activity .fit file
- `services/fit_file_service.py`: Device/device info spoofing via FIT file manipulation
- `services/garmin_service.py`: Handles authentication and upload to Garmin Connect
- `services/activity_processor.py`: End-to-end workflow orchestrator; single entrypoint for logic
- `main.py`: CLI entrypoint; configures logging, loads environment vars, runs ActivityProcessor

---

## Patterns to Follow

- **Service Initialization**: 
  - All API credentials must be injected (never hardcoded).
  - All major steps (Zwift, Garmin, FIT) use dependency injection and can be easily swapped or mocked.
- **Error Handling**:
  - Use standard Python exceptions. Log with proper `self.logger`.
  - Ensure temp files are always cleaned in the `finally` block in processors/services.

- **Zwift API**: Always use imports from `services.zwift` for modern usage:
  - Example: `from services.zwift import ZwiftClient`
  - Do not reintroduce/require zwift-client or protobuf anywhere.

- **Adding Services**:
  - Any new third-party API must have its own `services/<domain>_service.py` and be tested in isolation.

- **Testing**:
  - Tests live in `tests/`. One test file per service.
  - Mock external APIs with `responses` + `pytest-mock`.

---

## External Integration

- **Zwift API**: REST, modern endpoints, full OAuth flow. Credentials in `.env`.
- **Garmin Connect**: Via official Python library.
- **Environment**: All secrets in `.env`, never in code.
- **No codegen, no ORM**: All serialization is native (dicts/JSON). No database.

---

## Example Workflow

```python
from services.zwift import ZwiftClient
client = ZwiftClient("user", "pass")
profile = client.get_profile()
activities = profile.get_activities()
# ...
```

---

## House Rules

- Never add zwift-client, protobuf, or legacy/dead code.
- Do not touch `.env` in code—only read via `os.getenv` and dotenv.
- Use logging not print for info or debug output inside services.
- Keep all third-party boundaries in their dedicated service modules.

---
