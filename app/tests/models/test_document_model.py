"""Tests for document models."""

import pytest
from pydantic import ValidationError

from models.document_model import (
    FileMetadata,
    ProcessDocumentResponse,
    ValidationResponse,
    SupportedFormatsResponse
)


class TestFileMetadata:
    """Tests for FileMetadata model."""

    def test_file_metadata_creation(self):
        """Test creating a valid FileMetadata instance."""
        metadata = FileMetadata(
            filename='test.pdf',
            size_bytes=1024,
            size_mb=0.001,
            file_extension='pdf',
            is_supported=True
        )

        assert metadata.filename == 'test.pdf'
        assert metadata.size_bytes == 1024
        assert metadata.size_mb == 0.001
        assert metadata.file_extension == 'pdf'
        assert metadata.is_supported is True

    def test_file_metadata_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as excinfo:
            FileMetadata()

        error_details = excinfo.value.errors()
        required_fields = {error['loc'][0] for error in error_details}
        expected_fields = {
            'filename', 'size_bytes', 'size_mb',
            'file_extension', 'is_supported'
        }

        assert required_fields == expected_fields

    def test_file_metadata_field_types(self):
        """Test field type validation."""
        # Test invalid size_bytes (should be int)
        with pytest.raises(ValidationError):
            FileMetadata(
                filename='test.pdf',
                size_bytes='invalid',
                size_mb=0.001,
                file_extension='pdf',
                is_supported=True
            )

        # Test invalid size_mb (should be float)
        with pytest.raises(ValidationError):
            FileMetadata(
                filename='test.pdf',
                size_bytes=1024,
                size_mb='invalid',
                file_extension='pdf',
                is_supported=True
            )

        # Test invalid is_supported (should be bool)
        with pytest.raises(ValidationError):
            FileMetadata(
                filename='test.pdf',
                size_bytes=1024,
                size_mb=0.001,
                file_extension='pdf',
                is_supported='invalid'
            )

    def test_file_metadata_json_serialization(self):
        """Test JSON serialization of FileMetadata."""
        metadata = FileMetadata(
            filename='test.pdf',
            size_bytes=1024,
            size_mb=0.001,
            file_extension='pdf',
            is_supported=True
        )

        json_data = metadata.model_dump()

        assert json_data == {
            'filename': 'test.pdf',
            'size_bytes': 1024,
            'size_mb': 0.001,
            'file_extension': 'pdf',
            'is_supported': True
        }


class TestProcessDocumentResponse:
    """Tests for ProcessDocumentResponse model."""

    def test_process_document_response_creation(self):
        """Test creating a valid ProcessDocumentResponse."""
        metadata = FileMetadata(
            filename='test.pdf',
            size_bytes=1024,
            size_mb=0.001,
            file_extension='pdf',
            is_supported=True
        )

        response = ProcessDocumentResponse(
            markdown='# Test Document\n\nContent here',
            metadata=metadata,
        )

        assert response.markdown == '# Test Document\n\nContent here'
        assert response.metadata == metadata

    def test_process_document_response_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as excinfo:
            ProcessDocumentResponse()

        error_details = excinfo.value.errors()
        required_fields = {error['loc'][0] for error in error_details}
        expected_fields = {'markdown', 'metadata'}

        assert required_fields == expected_fields

    def test_process_document_response_nested_validation(self):
        """Test nested model validation."""
        # Test with invalid metadata
        with pytest.raises(ValidationError):
            ProcessDocumentResponse(
                markdown='# Test',
                metadata='invalid',
            )


class TestValidationResponse:
    """Tests for ValidationResponse model."""

    def test_validation_response_creation_minimal(self):
        """Test creating ValidationResponse with minimal required fields."""
        response = ValidationResponse(is_valid=True)

        assert response.is_valid is True
        assert response.filename is None
        assert response.is_supported_format is None
        assert response.error is None

    def test_validation_response_creation_full(self):
        """Test creating ValidationResponse with all fields."""
        response = ValidationResponse(
            is_valid=False,
            filename='test.xyz',
            is_supported_format=False,
            error='Unsupported format'
        )

        assert response.is_valid is False
        assert response.filename == 'test.xyz'
        assert response.is_supported_format is False
        assert response.error == 'Unsupported format'

    def test_validation_response_success_case(self):
        """Test ValidationResponse for successful validation."""
        response = ValidationResponse(
            is_valid=True,
            filename='document.pdf',
            is_supported_format=True,
            error=None
        )

        assert response.is_valid is True
        assert response.filename == 'document.pdf'
        assert response.is_supported_format is True
        assert response.error is None

    def test_validation_response_failure_case(self):
        """Test ValidationResponse for failed validation."""
        response = ValidationResponse(
            is_valid=False,
            filename='image.jpg',
            is_supported_format=False,
            error='Image formats are not supported'
        )

        assert response.is_valid is False
        assert response.filename == 'image.jpg'
        assert response.is_supported_format is False
        assert response.error == 'Image formats are not supported'


class TestSupportedFormatsResponse:
    """Tests for SupportedFormatsResponse model."""

    def test_supported_formats_response_creation(self):
        """Test creating a valid SupportedFormatsResponse."""
        response = SupportedFormatsResponse(
            supported_formats=['.pdf', '.docx', '.txt'],
            max_file_size_mb=10.0
        )

        assert response.supported_formats == ['.pdf', '.docx', '.txt']
        assert response.max_file_size_mb == 10.0

    def test_supported_formats_response_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError) as excinfo:
            SupportedFormatsResponse()

        error_details = excinfo.value.errors()
        required_fields = {error['loc'][0] for error in error_details}
        expected_fields = {'supported_formats', 'max_file_size_mb'}

        assert required_fields == expected_fields

    def test_supported_formats_response_empty_list(self):
        """Test SupportedFormatsResponse with empty formats list."""
        response = SupportedFormatsResponse(
            supported_formats=[],
            max_file_size_mb=10.0
        )

        assert response.supported_formats == []
        assert response.max_file_size_mb == 10.0

    def test_supported_formats_response_type_validation(self):
        """Test type validation for fields."""
        # Test invalid supported_formats type
        with pytest.raises(ValidationError):
            SupportedFormatsResponse(
                supported_formats='invalid',
                max_file_size_mb=10.0
            )

        # Test invalid max_file_size_mb type
        with pytest.raises(ValidationError):
            SupportedFormatsResponse(
                supported_formats=['.pdf'],
                max_file_size_mb='invalid'
            )


class TestModelInteroperability:
    """Tests for model interoperability and JSON operations."""

    def test_complete_workflow_serialization(self):
        """Test complete workflow with all models."""
        # Create a complete response
        metadata = FileMetadata(
            filename='document.pdf',
            size_bytes=2048,
            size_mb=0.002,
            file_extension='pdf',
            is_supported=True
        )

        response = ProcessDocumentResponse(
            markdown='# Converted Document\n\nContent here',
            metadata=metadata,
        )

        # Test JSON serialization
        json_data = response.model_dump()

        assert 'markdown' in json_data
        assert 'metadata' in json_data
        assert json_data['metadata']['filename'] == 'document.pdf'

    def test_model_from_dict(self):
        """Test creating models from dictionaries."""
        metadata_dict = {
            'filename': 'test.txt',
            'size_bytes': 512,
            'size_mb': 0.0005,
            'file_extension': 'txt',
            'is_supported': True
        }

        metadata = FileMetadata(**metadata_dict)

        assert metadata.filename == 'test.txt'
        assert metadata.size_bytes == 512

    def test_validation_response_edge_cases(self):
        """Test ValidationResponse edge cases."""
        # Test with empty string error
        response = ValidationResponse(
            is_valid=False,
            error=''
        )
        assert response.error == ''

        # Test with very long filename
        long_filename = 'a' * 255 + '.pdf'
        response = ValidationResponse(
            is_valid=True,
            filename=long_filename
        )
        assert response.filename == long_filename
