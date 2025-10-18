"""Tests for main_router_model.py."""

from models.main_router_model import OperationalStatus


class TestMainRouterModel:
    """Tests for OperationalStatus model."""

    def test_operational_status_model(self):
        """Test the OperationalStatus model instantiation and attributes."""
        status = OperationalStatus(operational=True)
        assert status.operational is True

        status = OperationalStatus(operational=False)
        assert status.operational is False
