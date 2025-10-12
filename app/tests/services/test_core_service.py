"""Tests for core service."""

import pytest
from unittest.mock import patch

from services.core_service import CoreService


class TestCoreService:
    """Tests for CoreService."""

    @pytest.fixture
    def service(self):
        """Create a CoreService instance."""
        return CoreService()

    def test_core_service_initialization(self, service):
        """Test CoreService initialization."""
        assert service is not None
        assert hasattr(service, 'markdown_processor')
        assert service.markdown_processor is not None

    def test_core_service_inheritance(self, service):
        """Test that CoreService inherits from DocumentMixinService."""
        # Test that it has methods from DocumentMixinService
        assert hasattr(service, 'get_supported_extensions')
        assert hasattr(service, 'validate_document')
        assert hasattr(service, 'process_document')
        assert hasattr(service, 'MAX_FILE_SIZE')
        assert hasattr(service, 'SUPPORTED_EXTENSIONS')

    def test_core_service_constants(self, service):
        """Test CoreService has the expected constants."""
        assert service.MAX_FILE_SIZE == 10 * 1024 * 1024  # 10MB
        assert isinstance(service.SUPPORTED_EXTENSIONS, set)
        assert '.pdf' in service.SUPPORTED_EXTENSIONS
        assert '.txt' in service.SUPPORTED_EXTENSIONS

    @patch('services.core_service.logger')
    def test_core_service_logging(self, mock_logger):
        """Test that CoreService logs initialization."""
        CoreService()
        mock_logger.info.assert_called_with(
            "CoreService initialized with Mixins capabilities."
        )

    def test_markdown_processor_type(self, service):
        """Test that markdown_processor is MarkItDown instance."""
        from markitdown import MarkItDown
        assert isinstance(service.markdown_processor, MarkItDown)
