# DocDrip API

A lightweight FastAPI-based service for converting documents to structured, markdown-friendly formats—drip by drip.

## Overview

DocDrip API provides a simple and efficient way to convert various document formats into markdown. Built with FastAPI, it offers a RESTful interface for document processing with support for multiple file types and comprehensive validation.

## Features

- 🚀 **Fast & Lightweight**: Built on FastAPI for high performance
- 📄 **Multi-format Support**: Convert various document types to markdown
- 🔒 **API Key Authentication**: Secure access with API key validation
- ✅ **Document Validation**: Pre-process validation without conversion
- 📊 **Detailed Metadata**: Rich information about processed files
- 🧪 **Comprehensive Testing**: Full test coverage with pytest
- 📚 **Auto Documentation**: Interactive API docs with OpenAPI/Swagger

## Requirements

- Python 3.11+
- pipenv (for dependency management)

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd docdrip-api
   ```

2. **Install dependencies**:

   ```bash
   pipenv install --dev
   ```

3. **Activate virtual environment**:

   ```bash
   pipenv shell
   ```

4. **Set up environment variables** (optional):

   ```bash
   cp .env.example .env  # Create from template if available
   ```

## Configuration

The API can be configured using environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_DEBUG` | `False` | Enable debug mode |
| `APP_VERSION` | `0.0.1` | API version |
| `APP_HOST` | `0.0.0.0` | Host address |
| `APP_PORT` | `8000` | Port number |
| `APP_SECRET_KEY` | `your-secret-key-here-change-this-in-production` | Secret key for security |

## Usage

### Starting the Server

```bash
# Development mode
pipenv run fastapi dev ./app/main.py  

# Production mode
pipenv run fastapi run --host 0.0.0.0 --port 8000
```

### Authentication

All document endpoints require API key authentication. Include your API key in the request headers:

```http
Authorization: Bearer your-api-key-here
```

## Development

### Project Structure

```text
docdrip-api/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── configs/             # Configuration management
│   ├── models/              # Pydantic models
│   ├── routers/             # API route handlers
│   │   └── v1/              # Version 1 API routes
│   └── services/            # Business logic services
├── tests/                   # Test suite
├── Pipfile                  # Dependencies
└── README.md
```

### Running Tests

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov=app

# Run specific test file
pipenv run pytest tests/test_main.py
```

### Code Quality

```bash
# Format code
pipenv run autopep8 --in-place --recursive app/

# Run tests with coverage
pipenv run pytest --cov=app --cov-report=html
```

## API Documentation

When running in debug mode, interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
