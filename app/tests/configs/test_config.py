"""Tests for config."""

import pytest
from pydantic import BaseModel

from configs.config import Config, SETTINGS


class TestConfig:
    """Tests for Config class."""

    @pytest.fixture
    def config_instance(self):
        """Create a Config instance."""
        return Config()

    def test_config_initialization(self, config_instance):
        """Test Config initialization."""
        assert config_instance is not None
        assert isinstance(config_instance, BaseModel)

    def test_config_attributes_exist_and_types(self, config_instance):
        """Test that config attributes exist and have expected types."""
        # String attributes
        assert hasattr(config_instance, 'APP_TITLE')
        assert isinstance(config_instance.APP_TITLE, str)

        assert hasattr(config_instance, 'APP_DESCRIPTION')
        assert isinstance(config_instance.APP_DESCRIPTION, str)

        # Optional string attributes (can be None or str)
        assert hasattr(config_instance, 'APP_VERSION')
        assert config_instance.APP_VERSION is None or isinstance(
            config_instance.APP_VERSION, str
        )

        assert hasattr(config_instance, 'APP_HOST')
        assert config_instance.APP_HOST is None or isinstance(
            config_instance.APP_HOST, str
        )

        assert hasattr(config_instance, 'APP_PORT')
        assert config_instance.APP_PORT is None or isinstance(
            config_instance.APP_PORT, str
        )

        assert hasattr(config_instance, 'APP_SECRET_KEY')
        assert config_instance.APP_SECRET_KEY is None or isinstance(
            config_instance.APP_SECRET_KEY, str
        )

        # Boolean property
        assert hasattr(config_instance, 'APP_DEBUG')
        assert isinstance(config_instance.APP_DEBUG, bool)

    def test_app_debug_property(self, config_instance):
        """Test APP_DEBUG property returns boolean."""
        debug_value = config_instance.APP_DEBUG
        assert isinstance(debug_value, bool)


class TestSettings:
    """Tests for SETTINGS singleton instance."""

    def test_settings_is_config_instance(self):
        """Test that SETTINGS is an instance of Config."""
        assert isinstance(SETTINGS, Config)

    def test_settings_has_required_attributes(self):
        """Test that SETTINGS has all required attributes with types."""
        assert hasattr(SETTINGS, 'APP_TITLE')
        assert isinstance(SETTINGS.APP_TITLE, str)

        assert hasattr(SETTINGS, 'APP_DESCRIPTION')
        assert isinstance(SETTINGS.APP_DESCRIPTION, str)

        assert hasattr(SETTINGS, 'APP_VERSION')
        assert SETTINGS.APP_VERSION is None or isinstance(
            SETTINGS.APP_VERSION, str
        )

        assert hasattr(SETTINGS, 'APP_HOST')
        assert SETTINGS.APP_HOST is None or isinstance(SETTINGS.APP_HOST, str)

        assert hasattr(SETTINGS, 'APP_PORT')
        assert SETTINGS.APP_PORT is None or isinstance(SETTINGS.APP_PORT, str)

        assert hasattr(SETTINGS, 'APP_SECRET_KEY')
        assert SETTINGS.APP_SECRET_KEY is None or isinstance(
            SETTINGS.APP_SECRET_KEY, str
        )

        assert hasattr(SETTINGS, 'APP_DEBUG')
        assert isinstance(SETTINGS.APP_DEBUG, bool)
