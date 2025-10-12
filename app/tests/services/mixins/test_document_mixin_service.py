"""Tests for document mixin service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from services.mixins.document_mixin_service import DocumentMixinService
from models.document_model import ValidationResponse


@pytest.fixture
def service():
    """Create a DocumentMixinService instance."""
    service = DocumentMixinService()
    service.markdown_processor = MagicMock()
    return service


@pytest.fixture
def mock_upload_file():
    """Create a mock UploadFile."""
    def _create_file(filename='test.txt', content=b'test'):
        mock_file = MagicMock()
        mock_file.filename = filename
        mock_file.read = AsyncMock(return_value=content)
        mock_file.seek = AsyncMock()
        return mock_file
    return _create_file


class TestDocumentMixinService:
    """Tests for DocumentMixinService."""

    def test_service_initialization(self, service):
        """Test that service can be initialized."""
        assert isinstance(service, DocumentMixinService)
        assert hasattr(service, 'markdown_processor')


class TestGetSupportedExtensions:
    """Tests for get_supported_extensions method."""

    def test_get_supported_extensions(self):
        """Test getting supported extensions."""
        service = DocumentMixinService()
        extensions = service.get_supported_extensions()

        assert isinstance(extensions, list)
        assert '.pdf' in extensions
        assert '.txt' in extensions
        assert '.docx' in extensions
        assert extensions == sorted(extensions)  # Should be sorted


class TestIsFileSupported:
    """Tests for _is_file_supported method."""

    def test_supported_file(self):
        """Test with supported file extension."""
        service = DocumentMixinService()
        assert service._is_file_supported('test.pdf') is True
        assert service._is_file_supported('document.docx') is True
        assert service._is_file_supported('readme.txt') is True

    def test_unsupported_file(self):
        """Test with unsupported file extension."""
        service = DocumentMixinService()
        assert service._is_file_supported('test.xyz') is False
        assert service._is_file_supported('image.jpg') is False

    def test_no_extension(self):
        """Test with file without extension."""
        service = DocumentMixinService()
        assert service._is_file_supported('README') is False


class TestValidateDocument:
    """Tests for validate_document method."""

    def test_validate_valid_file(self):
        """Test validation of valid file."""
        service = DocumentMixinService()
        mock_file = MagicMock()
        mock_file.filename = 'test.pdf'

        result = service.validate_document(mock_file)

        assert isinstance(result, ValidationResponse)
        assert result.is_valid is True
        assert result.filename == 'test.pdf'
        assert result.is_supported_format is True
        assert result.error is None

    def test_validate_invalid_file(self):
        """Test validation of invalid file."""
        service = DocumentMixinService()
        mock_file = MagicMock()
        mock_file.filename = 'test.xyz'

        result = service.validate_document(mock_file)

        assert isinstance(result, ValidationResponse)
        assert result.is_valid is False
        assert result.filename == 'test.xyz'
        assert result.is_supported_format is False
        assert 'Unsupported file format' in result.error

    def test_validate_no_file(self):
        """Test validation with no file."""
        service = DocumentMixinService()

        result = service.validate_document(None)

        assert result.is_valid is False
        assert 'File must be provided' in result.error

    def test_validate_no_filename(self):
        """Test validation with file but no filename."""
        service = DocumentMixinService()
        mock_file = MagicMock()
        mock_file.filename = None

        result = service.validate_document(mock_file)

        assert result.is_valid is False
        assert 'File must be provided' in result.error


class TestProcessDocument:
    """Tests for process_document method."""

    @pytest.mark.asyncio
    async def test_process_valid_document(self, service, mock_upload_file):
        """Test processing a valid document."""
        # Setup
        mock_file = mock_upload_file('test.txt', b'test content')
        mock_result = MagicMock()
        mock_result.text_content = '# Test\n\nConverted content'
        service.markdown_processor.convert.return_value = mock_result

        # Execute
        result = await service.process_document(mock_file)

        # Verify
        assert result.markdown == '# Test\n\nConverted content'
        assert result.metadata.filename == 'test.txt'
        assert result.processing_info.conversion_successful is True

    @pytest.mark.asyncio
    async def test_process_no_file(self, service):
        """Test processing with no file."""
        with pytest.raises(ValueError, match='Valid file with filename'):
            await service.process_document(None)

    @pytest.mark.asyncio
    async def test_process_unsupported_format(self, service, mock_upload_file):
        """Test processing unsupported file format."""
        mock_file = mock_upload_file('test.xyz', b'content')

        with pytest.raises(ValueError, match='Unsupported file format'):
            await service.process_document(mock_file)

    @pytest.mark.asyncio
    async def test_process_empty_file(self, service, mock_upload_file):
        """Test processing empty file."""
        mock_file = mock_upload_file('test.txt', b'')

        with pytest.raises(ValueError, match='File content is empty'):
            await service.process_document(mock_file)

    @pytest.mark.asyncio
    async def test_process_large_file(self, service, mock_upload_file):
        """Test processing file that's too large."""
        large_content = b'x' * (11 * 1024 * 1024)  # 11MB
        mock_file = mock_upload_file('test.txt', large_content)

        with pytest.raises(ValueError, match='File size.*exceeds maximum'):
            await service.process_document(mock_file)

    @pytest.mark.asyncio
    async def test_process_conversion_error(self, service, mock_upload_file):
        """Test processing with conversion error."""
        mock_file = mock_upload_file('test.txt', b'content')
        service.markdown_processor.convert.side_effect = Exception(
            'Conversion failed')

        with pytest.raises(Exception, match='Error during conversion'):
            await service.process_document(mock_file)
