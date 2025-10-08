# Zwift to Garmin Activity Transfer

A Python application that automatically transfers cycling activities from Zwift to Garmin Connect with proper device spoofing to ensure compatibility.

## 🏗️ Architecture

The application follows a clean, service-oriented architecture with clear separation of concerns:

### Service Classes

#### 1. **ZwiftService** (`services/zwift_service.py`)
- **Responsibility**: Handles Zwift authentication and activity downloads
- **Key Methods**:
  - `authenticate()` - Authenticates with Zwift API
  - `download_last_activity()` - Downloads the most recent activity as a FIT file

#### 2. **FitFileService** (`services/fit_file_service.py`)
- **Responsibility**: Manages FIT file modifications for device spoofing
- **Key Methods**:
  - `modify_device_info()` - Changes device manufacturer/product info
  - `cleanup_file()` - Removes temporary files

#### 3. **GarminService** (`services/garmin_service.py`)
- **Responsibility**: Handles Garmin Connect authentication and uploads
- **Key Methods**:
  - `authenticate()` - Authenticates with Garmin Connect
  - `upload_activity()` - Uploads FIT file to Garmin Connect

#### 4. **ActivityProcessor** (`services/activity_processor.py`)
- **Responsibility**: Orchestrates the complete workflow using dependency injection
- **Key Methods**:
  - `process_latest_activity()` - Executes the full transfer pipeline

## 🚀 Features

- **Clean Architecture**: Each service has a single responsibility
- **Dependency Injection**: Services are loosely coupled and easily testable
- **Comprehensive Error Handling**: Proper exception handling throughout
- **Extensive Testing**: 97% test coverage with 39 test cases
- **CI/CD Pipeline**: Automated testing on GitHub Actions
- **Device Spoofing**: Modifies FIT files to appear as Garmin Edge devices

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd zwift-to-garmin
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```env
ZWIFT_USERNAME=your_zwift_username
ZWIFT_PASSWORD=your_zwift_password
GARMIN_USERNAME=your_garmin_username
GARMIN_PASSWORD=your_garmin_password
```

## 🔧 Usage

Run the application:
```bash
python main.py
```

The application will:
1. Authenticate with Zwift and download your latest activity
2. Modify the FIT file to spoof device information (appears as Garmin Edge 530)
3. Upload the modified activity to Garmin Connect
4. Clean up temporary files

## 🧪 Testing

The project includes comprehensive testing with pytest:

### Run all tests:
```bash
pytest
```

### Run tests with coverage:
```bash
pytest --cov=services --cov-report=html --cov-report=term-missing
```

### Test Structure:
- `tests/test_zwift_service.py` - Tests for Zwift integration
- `tests/test_fit_file_service.py` - Tests for FIT file processing
- `tests/test_garmin_service.py` - Tests for Garmin integration
- `tests/test_activity_processor.py` - Tests for workflow orchestration
- `tests/test_main.py` - Tests for main entry point

## 🏃‍♂️ CI/CD

The project includes a GitHub Actions workflow (`.github/workflows/build.yml`) that:

- **Multi-Python Testing**: Tests against Python 3.9, 3.10, 3.11, and 3.12
- **Code Quality**: Runs flake8 linting
- **Test Coverage**: Generates coverage reports
- **Security Scanning**: Uses safety and bandit for security checks
- **Dependency Caching**: Optimizes build times

### Workflow Triggers:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

## 🛠️ Development

### Adding New Features:
1. Create service classes following the single responsibility principle
2. Add comprehensive unit tests
3. Use dependency injection for loose coupling
4. Follow the existing error handling patterns

### Testing Best Practices:
- Mock external dependencies (APIs, file system)
- Test both success and failure scenarios
- Use descriptive test names and docstrings
- Maintain high test coverage (>95%)

## 📋 Dependencies

### Core Dependencies:
- `fit-tool` - FIT file manipulation
- `garminconnect` - Garmin Connect API integration
- `zwift-client` - Zwift API integration
- `requests` - HTTP client
- `python-dotenv` - Environment variable management

### Testing Dependencies:
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `responses` - HTTP response mocking

## 🔒 Security

- Credentials are managed via environment variables
- No sensitive data is logged or stored
- Dependencies are scanned for vulnerabilities
- Code is analyzed with security linting tools

## 📝 Error Handling

Each service implements robust error handling:
- **Authentication errors**: Clear error messages for invalid credentials
- **Network errors**: Retry logic and connection error handling
- **File errors**: Proper cleanup of temporary files
- **API errors**: Specific handling for rate limits and service unavailability

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

The CI pipeline will automatically run tests and code quality checks on your PR.

## 📄 License

[Add your license information here]
