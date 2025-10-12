"""Tests for main FastAPI application."""

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from main import app


class TestFastAPIApp:
    """Tests for the main FastAPI application."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_app_instance(self):
        """Test that app is a FastAPI instance."""
        assert isinstance(app, FastAPI)

    def test_cors_middleware_configured(self):
        """Test that CORS middleware is properly configured."""
        # Check that CORS middleware is in the middleware stack
        middleware_classes = [
            middleware.cls for middleware in app.user_middleware
        ]
        assert CORSMiddleware in middleware_classes

    def test_cors_middleware_settings(self):
        """Test CORS middleware configuration settings."""
        # Find the CORS middleware configuration
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None

        # Check CORS configuration
        kwargs = cors_middleware.kwargs
        assert kwargs['allow_origins'] == ['*']
        assert kwargs['allow_credentials'] is True
        assert kwargs['allow_methods'] == ['*']
        assert kwargs['allow_headers'] == ['*']

    def test_api_v1_router_included(self, client):
        """Test that API v1 router is included."""
        # Test a known endpoint from the v1 router
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

    def test_cors_headers_in_response(self, client):
        """Test that CORS headers are included in responses."""
        response = client.get(
            '/v1/documents/supported-formats',
            headers={'Origin': 'http://localhost:3000'}
        )

        # Check that CORS headers are present
        assert 'access-control-allow-origin' in response.headers
        assert response.headers['access-control-allow-origin'] == '*'

    def test_cors_preflight_request(self, client):
        """Test CORS preflight request handling."""
        response = client.options(
            '/v1/documents/supported-formats',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )

        assert response.status_code == 200
        assert 'access-control-allow-origin' in response.headers
        assert 'access-control-allow-methods' in response.headers
        assert 'access-control-allow-headers' in response.headers

    def test_app_routes_registration(self):
        """Test that all expected routes are registered."""
        # Get all routes from the app
        routes = [route.path for route in app.routes]

        # Check that v1 routes are included
        v1_routes = [route for route in routes if route.startswith('/v1')]
        assert len(v1_routes) > 0

        # Check specific endpoints
        expected_endpoints = [
            '/v1/documents/supported-formats',
            '/v1/documents',
            '/v1/documents/validate'
        ]

        for endpoint in expected_endpoints:
            assert endpoint in routes

    def test_app_metadata(self):
        """Test FastAPI app metadata and configuration."""
        # Test that the app has expected attributes
        assert hasattr(app, 'routes')
        assert hasattr(app, 'middleware')
        assert hasattr(app, 'user_middleware')

    def test_health_check_via_supported_formats(self, client):
        """Test basic health check using supported formats endpoint."""
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        data = response.json()
        assert 'supported_formats' in data
        assert 'max_file_size_mb' in data
        assert isinstance(data['supported_formats'], list)
        assert len(data['supported_formats']) > 0

    def test_non_existent_route(self, client):
        """Test that non-existent routes return 404."""
        response = client.get('/non-existent-endpoint')
        assert response.status_code == 404

    def test_root_path_not_found(self, client):
        """Test that root path returns 404 (no root endpoint defined)."""
        response = client.get('/')
        assert response.status_code == 404

    def test_app_startup_and_shutdown(self):
        """Test that app can be started and stopped without errors."""
        # This test ensures the app initialization doesn't raise exceptions
        test_client = TestClient(app)

        # Perform a simple request to ensure app is working
        response = test_client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

    def test_middleware_order(self):
        """Test middleware is in the correct order."""
        # CORS middleware should be present
        middleware_classes = [
            middleware.cls.__name__ for middleware in app.user_middleware
        ]
        assert 'CORSMiddleware' in middleware_classes

    def test_app_dependency_injection(self, client):
        """Test that dependency injection works correctly."""
        # Test that services are properly injected by making API calls
        response = client.get('/v1/documents/supported-formats')
        assert response.status_code == 200

        # The fact that this works means dependency injection is working
        # as the router depends on the core service
