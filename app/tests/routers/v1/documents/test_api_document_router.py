"""Tests for document API router."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import io

from main import app


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_file():
    """Create a mock file for testing."""
    def _create_file(filename='test.txt', content=b'test content'):
        return ('file', (filename, io.BytesIO(content), 'text/plain'))
    return _create_file


class TestGetSupportedFormats:
    """Tests for the get supported formats endpoint."""

    def test_get_supported_formats_success(self, client):
        """Test getting supported formats returns 200."""
        response = client.get('/v1/documents/supported-formats')

        assert response.status_code == 200
        data = response.json()
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data
        assert isinstance(data['supported_formats'], list)
        assert isinstance(data['max_file_size_mb'], (int, float))

    def test_get_supported_formats_response_structure(self, client):
        """Test the structure of supported formats response."""
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()

        # Check required fields
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data

        # Check data types
        assert isinstance(data['supported_formats'], list)
        assert isinstance(data['max_file_size_mb'], (int, float))

        # Check that we have some supported formats
        assert len(data['supported_formats']) > 0

        # Check that max file size is reasonable
        assert data['max_file_size_mb'] > 0

    def test_get_supported_formats_content(self, client):
        """Test the content of supported formats response."""
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()
        formats = data['supported_formats']

        # Check that common formats are supported
        expected_formats = ['.pdf', '.txt', '.docx']
        for fmt in expected_formats:
            assert fmt in formats

        # Check max file size (should be 10MB = 10.0)
        assert data['max_file_size_mb'] == 10.0

    def test_get_supported_formats_headers(self, client):
        """Test response headers for supported formats endpoint."""
        response = client.get(
            '/v1/documents/supported-formats',
            headers={'Origin': 'http://localhost:3000'}
        )
        assert response.status_code == 200

        # Check content type
        assert response.headers['content-type'] == 'application/json'

        # Check CORS headers
        assert 'access-control-allow-origin' in response.headers

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_get_supported_formats_service_integration(
        self, mock_service, client
    ):
        """Test service integration for supported formats."""
        # Mock service response
        mock_service.get_supported_extensions.return_value = [
            '.pdf', '.txt', '.docx'
        ]
        mock_service.MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()
        assert data['supported_formats'] == ['.pdf', '.txt', '.docx']
        assert data['max_file_size_mb'] == 5.0

        # Verify service method was called
        mock_service.get_supported_extensions.assert_called_once()


class TestConvertDocument:
    """Tests for the convert document endpoint."""

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_success(self, mock_service, client, mock_file):
        """Test successful document conversion."""
        # Import models for proper structure
        from models.document_model import (
            ProcessDocumentResponse, FileMetadata, ProcessingInfo
        )

        # Create properly structured mock response using actual models
        metadata = FileMetadata(
            filename='test.txt',
            size_bytes=1024,
            size_mb=0.001,
            file_extension='txt',
            is_supported=True
        )

        processing_info = ProcessingInfo(
            supported_formats=['.txt', '.pdf', '.docx'],
            max_file_size_mb=10.0,
            conversion_successful=True
        )

        mock_response = ProcessDocumentResponse(
            markdown='# Test Document\n\nConverted content',
            metadata=metadata,
            processing_info=processing_info
        )

        # Use AsyncMock for the async process_document method
        from unittest.mock import AsyncMock
        mock_service.process_document = AsyncMock(return_value=mock_response)

        files = [mock_file('test.txt', b'test content')]
        response = client.post('/v1/documents', files=files)

        assert response.status_code == 200
        mock_service.process_document.assert_called_once()

        # Check response structure
        data = response.json()
        assert 'markdown' in data
        assert 'metadata' in data
        assert 'processing_info' in data

    def test_convert_document_no_file(self, client):
        """Test conversion without file returns 422."""
        response = client.post('/v1/documents')
        assert response.status_code == 422

    def test_convert_document_empty_filename(self, client):
        """Test conversion with empty filename."""
        files = [('file', ('', io.BytesIO(b'content'), 'text/plain'))]
        response = client.post('/v1/documents', files=files)
        # Should return an error due to empty filename
        assert response.status_code in [400, 422]

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_value_error(
        self, mock_service, client, mock_file
    ):
        """Test conversion with invalid file returns 400."""
        from unittest.mock import AsyncMock
        mock_service.process_document = AsyncMock(
            side_effect=ValueError('Invalid file format')
        )

        files = [mock_file('test.xyz')]
        response = client.post('/v1/documents', files=files)

        assert response.status_code == 400
        data = response.json()
        assert 'Invalid file format' in data['detail']

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_server_error(
        self,
        mock_service,
        client,
        mock_file
    ):
        """Test conversion with server error returns 500."""
        from unittest.mock import AsyncMock
        mock_service.process_document = AsyncMock(
            side_effect=Exception('Processing failed')
        )

        files = [mock_file('test.txt')]
        response = client.post('/v1/documents', files=files)

        assert response.status_code == 500
        data = response.json()
        assert 'Error converting document' in data['detail']
        assert 'Processing failed' in data['detail']

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_convert_document_large_file(
        self,
        mock_service,
        client,
        mock_file
    ):
        """Test conversion with large file."""
        from unittest.mock import AsyncMock
        mock_service.process_document = AsyncMock(
            side_effect=ValueError('File size exceeds maximum allowed size')
        )

        files = [mock_file('large.txt', b'x' * (11 * 1024 * 1024))]  # 11MB
        response = client.post('/v1/documents', files=files)

        assert response.status_code == 400
        data = response.json()
        assert 'File size' in data['detail']

    def test_convert_document_multiple_files(self, client, mock_file):
        """Test conversion with multiple files (should only process first)."""
        files = [
            mock_file('test1.txt', b'content1'),
            mock_file('test2.txt', b'content2')
        ]
        response = client.post('/v1/documents', files=files)

        # Should process the first file or return an error
        # The exact behavior depends on FastAPI's file handling
        assert response.status_code in [200, 400, 422]


class TestValidateDocument:
    """Tests for the validate document endpoint."""

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_success(self, mock_service, client, mock_file):
        """Test successful document validation."""
        from models.document_model import ValidationResponse

        mock_response = ValidationResponse(
            is_valid=True,
            filename='test.pdf',
            is_supported_format=True,
            error=None
        )
        mock_service.validate_document.return_value = mock_response

        files = [mock_file('test.pdf')]
        response = client.post('/v1/documents/validate', files=files)

        assert response.status_code == 200
        mock_service.validate_document.assert_called_once()

        data = response.json()
        assert data['is_valid'] is True
        assert data['filename'] == 'test.pdf'
        assert data['is_supported_format'] is True
        assert data['error'] is None

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_invalid_format(
        self,
        mock_service,
        client,
        mock_file
    ):
        """Test validation of unsupported document format."""
        from models.document_model import ValidationResponse

        mock_response = ValidationResponse(
            is_valid=False,
            filename='test.xyz',
            is_supported_format=False,
            error='Unsupported file format'
        )
        mock_service.validate_document.return_value = mock_response

        files = [mock_file('test.xyz')]
        response = client.post('/v1/documents/validate', files=files)

        assert response.status_code == 200
        data = response.json()
        assert data['is_valid'] is False
        assert data['filename'] == 'test.xyz'
        assert data['is_supported_format'] is False
        assert 'Unsupported file format' in data['error']

    def test_validate_document_no_file(self, client):
        """Test validation without file returns 422."""
        response = client.post('/v1/documents/validate')
        assert response.status_code == 422

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_server_error(
        self,
        mock_service,
        client,
        mock_file
    ):
        """Test validation with server error returns 500."""
        mock_service.validate_document.side_effect = Exception(
            'Validation failed')

        files = [mock_file('test.txt')]
        response = client.post('/v1/documents/validate', files=files)

        assert response.status_code == 500
        data = response.json()
        assert 'Error validating document' in data['detail']
        assert 'Validation failed' in data['detail']

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_validate_document_response_structure(
        self,
        mock_service,
        client,
        mock_file
    ):
        """Test validation response structure."""
        from models.document_model import ValidationResponse

        mock_response = ValidationResponse(
            is_valid=True,
            filename='test.pdf',
            is_supported_format=True,
            error=None
        )
        mock_service.validate_document.return_value = mock_response

        files = [mock_file('test.pdf')]
        response = client.post('/v1/documents/validate', files=files)

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        required_fields = ['is_valid', 'filename',
                           'is_supported_format', 'error']
        for field in required_fields:
            assert field in data

    def test_validate_document_headers(self, client, mock_file):
        """Test response headers for validation endpoint."""
        files = [mock_file('test.pdf')]
        response = client.post(
            '/v1/documents/validate',
            files=files,
            headers={'Origin': 'http://localhost:3000'}
        )

        # Should return 200 or error, but should have proper headers
        assert 'content-type' in response.headers
        assert 'access-control-allow-origin' in response.headers


class TestDocumentRouterIntegration:
    """Integration tests for the document router."""

    def test_all_endpoints_accessible(self, client):
        """Test that all document endpoints are accessible."""
        # GET endpoint
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # POST endpoints (should return 422 without files, not 404)
        response = client.post('/v1/documents')
        assert response.status_code == 422

        response = client.post('/v1/documents/validate')
        assert response.status_code == 422

    def test_router_error_handling_consistency(self, client, mock_file):
        """Test consistent error handling across endpoints."""
        # All endpoints should return proper JSON error responses
        endpoints = [
            ('/v1/documents', 'post'),
            ('/v1/documents/validate', 'post')
        ]

        for endpoint, method in endpoints:
            if method == 'post':
                response = client.post(endpoint)
            else:
                response = client.get(endpoint)

            # Should return JSON error
            assert 'application/json' in response.headers['content-type']

            # Should have detail field in error response
            if response.status_code >= 400:
                data = response.json()
                assert 'detail' in data

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_service_dependency_injection(self, mock_service, client):
        """Test that service is properly injected and shared."""
        # Mock service
        mock_service.get_supported_extensions.return_value = ['.pdf']
        mock_service.MAX_FILE_SIZE = 1024 * 1024

        # Call multiple endpoints
        response1 = client.get('/v1/documents/supported-formats')
        assert response1.status_code == 200

        # Service should be called
        assert mock_service.get_supported_extensions.called

    def test_openapi_documentation_generation(self, client):
        """Test that router contributes to OpenAPI docs."""
        response = client.get('/openapi.json')
        assert response.status_code == 200

        openapi_data = response.json()
        paths = openapi_data.get('paths', {})

        # Check document endpoints are documented
        assert '/v1/documents/supported-formats' in paths
        assert '/v1/documents' in paths
        assert '/v1/documents/validate' in paths

        # Check HTTP methods are documented
        assert 'get' in paths['/v1/documents/supported-formats']
        assert 'post' in paths['/v1/documents']
        assert 'post' in paths['/v1/documents/validate']
