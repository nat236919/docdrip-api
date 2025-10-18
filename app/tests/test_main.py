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
