"""Tests for document API router."""

import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app
from configs.config import SETTINGS


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def authenticated_client():
    """Test client with authentication headers."""
    return TestClient(app, headers={'X-API-Key': SETTINGS.APP_SECRET_KEY})


@pytest.fixture
def mock_file():
    """Create a mock file for testing."""
    def _create_file(filename='test.txt', content=b'test content'):
        return ('file', (filename, io.BytesIO(content), 'text/plain'))
    return _create_file


class TestGetSupportedFormats:
    """Tests for the get supported formats endpoint."""

    def test_get_supported_formats(self, authenticated_client):
        """Test getting supported formats returns correct structure."""
        response = authenticated_client.get('/v1/documents/supported-formats')

        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/json'

        data = response.json()
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data
        assert isinstance(data['supported_formats'], list)
        assert isinstance(data['max_file_size_mb'], (int, float))
        assert len(data['supported_formats']) > 0
        assert data['max_file_size_mb'] > 0

        # Check common formats are supported
        expected_formats = ['.pdf', '.txt', '.docx']
        for fmt in expected_formats:
            assert fmt in data['supported_formats']

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_get_supported_formats_service_integration(
        self, mock_service, authenticated_client
    ):
        """Test service integration for supported formats."""
        mock_service.get_supported_extensions.return_value = ['.pdf', '.txt']
        mock_service.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        response = authenticated_client.get('/v1/documents/supported-formats')

        assert response.status_code == 200
        data = response.json()
        assert data['supported_formats'] == ['.pdf', '.txt']
        assert data['max_file_size_mb'] == 5.0
        mock_service.get_supported_extensions.assert_called_once()


class TestConvertDocument:
    """Tests for the convert document endpoint."""

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_success(
        self, mock_service, authenticated_client, mock_file
    ):
        """Test successful document conversion."""
        from models.document_model import (
            ProcessDocumentResponse, FileMetadata, ProcessingInfo
        )

        # Create mock response
        metadata = FileMetadata(
            filename='test.txt', size_bytes=1024, size_mb=0.001,
            file_extension='txt', is_supported=True
        )
        processing_info = ProcessingInfo(
            supported_formats=['.txt', '.pdf'], max_file_size_mb=10.0,
            conversion_successful=True
        )
        mock_response = ProcessDocumentResponse(
            markdown='# Test\nContent', metadata=metadata,
            processing_info=processing_info
        )
        mock_service.process_document = AsyncMock(return_value=mock_response)

        files = [mock_file('test.txt', b'test content')]
        response = authenticated_client.post('/v1/documents', files=files)

        assert response.status_code == 200
        mock_service.process_document.assert_called_once()

        data = response.json()
        expected_keys = ['markdown', 'metadata', 'processing_info']
        assert all(key in data for key in expected_keys)

    def test_convert_document_no_file(self, authenticated_client):
        """Test conversion without file returns 422."""
        response = authenticated_client.post('/v1/documents')
        assert response.status_code == 422

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_errors(
        self, mock_service, authenticated_client, mock_file
    ):
        """Test conversion error handling."""

        # Test ValueError (400)
        mock_service.process_document = AsyncMock(
            side_effect=ValueError('Invalid file format')
        )
        files = [mock_file('test.xyz')]
        response = authenticated_client.post('/v1/documents', files=files)
        assert response.status_code == 400
        assert 'Invalid file format' in response.json()['detail']

        # Test generic error (500)
        mock_service.process_document = AsyncMock(
            side_effect=Exception('Processing failed')
        )
        files = [mock_file('test.txt')]
        response = authenticated_client.post('/v1/documents', files=files)
        assert response.status_code == 500
        assert 'Error converting document' in response.json()['detail']


class TestValidateDocument:
    """Tests for the validate document endpoint."""

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_success(
        self, mock_service, authenticated_client, mock_file
    ):
        """Test successful document validation."""
        from models.document_model import ValidationResponse

        mock_response = ValidationResponse(
            is_valid=True, filename='test.pdf', is_supported_format=True,
            error=None
        )
        mock_service.validate_document.return_value = mock_response

        files = [mock_file('test.pdf')]
        response = authenticated_client.post(
            '/v1/documents/validate', files=files
        )

        assert response.status_code == 200
        mock_service.validate_document.assert_called_once()

        data = response.json()
        assert data['is_valid'] is True
        assert data['filename'] == 'test.pdf'
        assert data['is_supported_format'] is True
        assert data['error'] is None
        assert 'content-type' in response.headers

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_invalid(
        self, mock_service, authenticated_client, mock_file
    ):
        """Test validation of unsupported document format."""
        from models.document_model import ValidationResponse

        mock_response = ValidationResponse(
            is_valid=False, filename='test.xyz', is_supported_format=False,
            error='Unsupported file format'
        )
        mock_service.validate_document.return_value = mock_response

        files = [mock_file('test.xyz')]
        response = authenticated_client.post(
            '/v1/documents/validate', files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data['is_valid'] is False
        assert 'Unsupported file format' in data['error']

    def test_validate_document_no_file(self, authenticated_client):
        """Test validation without file returns 422."""
        response = authenticated_client.post('/v1/documents/validate')
        assert response.status_code == 422

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_server_error(
        self, mock_service, authenticated_client, mock_file
    ):
        """Test validation with server error returns 500."""
        mock_service.validate_document.side_effect = Exception(
            'Validation failed'
        )

        files = [mock_file('test.txt')]
        response = authenticated_client.post(
            '/v1/documents/validate', files=files
        )

        assert response.status_code == 500
        data = response.json()
        assert 'Error validating document' in data['detail']


class TestDocumentRouterIntegration:
    """Integration tests for the document router."""

    def test_all_endpoints_accessible(self, authenticated_client):
        """Test that all document endpoints are accessible."""
        # GET endpoint
        response = authenticated_client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # POST endpoints (should return 422 without files, not 404)
        for endpoint in ['/v1/documents', '/v1/documents/validate']:
            response = authenticated_client.post(endpoint)
            assert response.status_code == 422
            assert 'application/json' in response.headers['content-type']

    def test_openapi_documentation_generation(self, authenticated_client):
        """Test that router contributes to OpenAPI docs."""
        response = authenticated_client.get('/openapi.json')
        assert response.status_code == 200

        paths = response.json().get('paths', {})
        expected_paths = [
            '/v1/documents/supported-formats',
            '/v1/documents',
            '/v1/documents/validate'
        ]

        for path in expected_paths:
            assert path in paths
