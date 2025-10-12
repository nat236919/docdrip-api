"""Tests for main API router."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


class TestApiMainRouter:
    """Tests for API v1 main router."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_router_includes_document_routes(self, client):
        """Test that main router includes document routes."""
        # Test that document endpoints are accessible through v1 prefix
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

    def test_router_prefix(self, client):
        """Test that router has correct v1 prefix."""
        # Should work with v1 prefix
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # Should not work without v1 prefix
        response = client.get('/documents/supported-formats')
        assert response.status_code == 404

    def test_router_integration(self, client):
        """Test router integration with main app."""
        # Test that all document endpoints are accessible
        endpoints = [
            '/v1/documents/supported-formats',
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not be 404 (route exists)
            assert response.status_code != 404

    def test_router_tags_and_metadata(self):
        """Test that router has correct tags and metadata."""
        # Check that the router is properly configured in the main app
        v1_routes = [
            route for route in app.routes
            if hasattr(route, 'path') and route.path.startswith('/v1')
        ]
        assert len(v1_routes) > 0

    def test_all_document_endpoints_accessible(self, client):
        """Test that all document endpoints are accessible."""
        # Test GET endpoint
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # Test POST endpoints exist (even if they return errors without files)
        response = client.post('/v1/documents')
        assert response.status_code in [400, 422]  # Expected without file

        response = client.post('/v1/documents/validate')
        assert response.status_code in [400, 422]  # Expected without file

    def test_router_error_handling_integration(self, client):
        """Test that router properly handles errors through the main app."""
        # Test that errors are properly propagated through the router chain
        response = client.get('/v1/non-existent-endpoint')
        assert response.status_code == 404

    def test_router_cors_integration(self, client):
        """Test that CORS works correctly with the router."""
        response = client.get(
            '/v1/documents/supported-formats',
            headers={'Origin': 'http://localhost:3000'}
        )
        assert response.status_code == 200

        # Check CORS headers are present
        assert 'access-control-allow-origin' in response.headers

    def test_router_dependency_injection(self, client):
        """Test that dependencies are properly injected through the router."""
        # The core service should be available to the document router
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data

    @patch('routers.v1.documents.api_document_router.core_service')
    def test_router_service_interaction(self, mock_service, client):
        """Test that router properly interacts with services."""
        # Mock service response
        mock_service.get_supported_extensions.return_value = ['.pdf', '.txt']
        mock_service.MAX_FILE_SIZE = 10 * 1024 * 1024

        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # Verify service method was called
        mock_service.get_supported_extensions.assert_called_once()

    def test_router_response_models(self, client):
        """Test that router endpoints return properly structured responses."""
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()

        # Verify response structure matches SupportedFormatsResponse model
        assert isinstance(data, dict)
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data
        assert isinstance(data['supported_formats'], list)
        assert isinstance(data['max_file_size_mb'], (int, float))

    def test_router_openapi_documentation(self):
        """Test that router contributes to OpenAPI documentation."""
        # Get the OpenAPI schema
        with TestClient(app) as test_client:
            response = test_client.get('/openapi.json')
            assert response.status_code == 200

            openapi_data = response.json()
            paths = openapi_data.get('paths', {})

            # Check that v1 document endpoints are documented
            assert '/v1/documents/supported-formats' in paths
            assert '/v1/documents' in paths
            assert '/v1/documents/validate' in paths
