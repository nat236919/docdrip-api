"""Tests for auth service."""

import pytest
from unittest.mock import patch
from fastapi import HTTPException, status

from services.auth_service import AuthService


class TestAuthService:
    """Tests for AuthService."""

    @pytest.fixture
    def mock_settings(self):
        """Mock settings with test API key."""
        with patch('services.auth_service.SETTINGS') as mock:
            mock.APP_SECRET_KEY = 'test-secret-key-123'
            yield mock

    @pytest.fixture
    def auth_service(self, mock_settings):
        """Create an AuthService instance with mocked settings."""
        return AuthService()

    def test_auth_service_initialization(self, auth_service, mock_settings):
        """Test AuthService initialization."""
        assert auth_service is not None
        assert auth_service.api_key == 'test-secret-key-123'

    def test_validate_api_key_valid(self, auth_service):
        """Test validate_api_key with valid API key."""
        result = auth_service.validate_api_key('test-secret-key-123')
        assert result is True

    def test_validate_api_key_invalid_key(self, auth_service):
        """Test validate_api_key with invalid API key."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_api_key('invalid-key')

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Unauthorized'

    def test_validate_api_key_empty_key(self, auth_service):
        """Test validate_api_key with empty API key."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_api_key('')

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Unauthorized'

    def test_validate_api_key_none_key(self, auth_service):
        """Test validate_api_key with None API key."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_api_key(None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Unauthorized'

    def test_validate_api_key_whitespace_key(self, auth_service):
        """Test validate_api_key with whitespace-only API key."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_api_key('   ')

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Unauthorized'

    def test_validate_api_key_type_conversion(self, auth_service):
        """Test validate_api_key with string conversion."""
        # Test that integer keys are converted to string for comparison
        with patch.object(auth_service, 'api_key', '123'):
            result = auth_service.validate_api_key(123)
            assert result is True

    def test_validate_api_key_case_sensitive(self, auth_service):
        """Test validate_api_key is case sensitive."""
        with pytest.raises(HTTPException) as exc_info:
            auth_service.validate_api_key('TEST-SECRET-KEY-123')

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == 'Unauthorized'

    @patch('services.auth_service.SETTINGS')
    def test_auth_service_with_different_secret(self, mock_settings):
        """Test AuthService with different secret key."""
        mock_settings.APP_SECRET_KEY = 'different-secret'
        service = AuthService()

        assert service.api_key == 'different-secret'
        assert service.validate_api_key('different-secret') is True

        with pytest.raises(HTTPException):
            service.validate_api_key('test-secret-key-123')
