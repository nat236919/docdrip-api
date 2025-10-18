"""Tests for main API router."""

import pytest
from fastapi.testclient import TestClient

from main import app
from models.main_router_model import OperationalStatus


class TestApiMainRouter:
    """Tests for API v1 main router."""

    @pytest.fixture
    def client(self):
        """Test client for the FastAPI app."""
        return TestClient(app)

    def test_v1_endpoint(self, client):
        """Test the /v1 endpoint."""
        response = client.get('/v1')
        assert response.status_code == 200

        response_data = OperationalStatus(**response.json())
        assert response_data.operational is True
