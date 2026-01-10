# Zwift to Garmin Activity Transfer

A robust and fully open-source Python application that automatically transfers cycling activities from Zwift to Garmin Connect—including device spoofing for seamless compatibility.

---

## 🚦 Features

- **Modern Zwift API Client** — No legacy dependencies, no zwift-client, zero protobuf required.
- **Service-Oriented Architecture** — Modular, testable, single-responsibility Python services.
- **Device Spoofing** — Activities appear as if from a real Garmin Edge.
- **Comprehensive Test Coverage** — All modules covered; easy to run and expand tests.
- **.env & Security** — All credentials handled securely via environment variables.
- **Robust Error Handling** — Clean and descriptive logging for all API and file ops.

---

## 🛠️ Project Structure

```
services/
├─ zwift/              # Modern modular Zwift API client (auth, activities, requests, etc)
├─ zwift_service.py    # Downloads activities from Zwift
├─ fit_file_service.py # Device spoofing and file mangling
├─ garmin_service.py   # Uploads to Garmin Connect
├─ activity_processor.py  # Orchestrates full Zwift→Garmin workflow
main.py                # CLI entry point
```

Tests: See `tests/`, with tests for every service and API.

---

## ⏬ Installation

1. **Clone and enter project directory:**
   ```bash
   git clone <repository-url>
   cd zwift-to-garmin
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   Create a `.env` file with Zwift and Garmin credentials:
   ```dotenv
   ZWIFT_USERNAME=your_zwift_username
   ZWIFT_PASSWORD=your_zwift_password
   GARMIN_USERNAME=your_garmin_username
   GARMIN_PASSWORD=your_garmin_password
   ```

---

## 🚀 Usage

```bash
python main.py
```

- Downloads your latest Zwift activity (after authenticating).
- Modifies the FIT file to spoof device info (mimics a Garmin Edge).
- Uploads the activity to Garmin Connect.
- Cleans up all temp files.

---

## 🧪 Testing

Run the whole suite:

```bash
pytest -v
```

For coverage:

```bash
pytest --cov=services --cov-report=html
```

**Test structure:**  
All major services and features have their dedicated test files under `tests/`.

---

## 📚 Key Services & Public APIs

- `ZwiftService`: Authenticates and downloads activities from Zwift (see `services/zwift/` for modular API).
- `FitFileService`: Modifies and cleans up FIT files.
- `GarminService`: Authenticates and uploads activities to Garmin Connect.
- `ActivityProcessor`: Orchestrates the full process.

**The Zwift API client is a brand-new, fully modular implementation; no legacy or 3rd-party zwift-client or protobuf required.**

---

## 🔒 Security

- Credentials *never* logged or saved; use `.env`.
- All dependencies are up-to-date and scanned.

---

## 🤝 Contributing

1. Fork, branch, and develop new features as modular services.
2. Add or update tests for all changes.
3. Open a PR—CI/CD will verify tests and quality.

