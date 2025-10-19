import io
import logging
from pathlib import Path
from typing import List

from fastapi import UploadFile

from models.document_model import (
    FileMetadata,
    ProcessDocumentResponse,
    ValidationResponse
)


logger = logging.getLogger(__name__)


class DocumentMixinService:
    """Mixin class providing document-specific functionality."""

    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.txt', '.md', '.html', '.htm',
        '.xlsx', '.xls', '.pptx', '.ppt', '.rtf'
    }

    # ========================================
    # Public Methods
    # ========================================

    async def process_document(
        self, file: UploadFile
    ) -> ProcessDocumentResponse:
        """Process a document file.

        Args:
            file (UploadFile): The uploaded file to process.

        Returns:
            ProcessDocumentResponse: A response containing the converted
                markdown content, file metadata, and processing information.

        Raises:
            ValueError: If the file is invalid or unsupported.
            Exception: If there is an error during processing.
        """
        if not file or not file.filename:
            raise ValueError('Valid file with filename must be provided.')

        logger.info(f'Processing document: {file.filename}')

        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            supported_formats = ', '.join(sorted(self.SUPPORTED_EXTENSIONS))
            raise ValueError(
                f'Unsupported file format: {file_extension}. '
                f'Supported formats: {supported_formats}'
            )

        # Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f'Error reading file {file.filename}: {str(e)}')
            raise Exception(f'Error reading file: {str(e)}')
        finally:
            # Reset file position for potential future reads
            await file.seek(0)

        # Validate file content
        if not file_content:
            raise ValueError('File content is empty.')

        # Validate file size
        if len(file_content) > self.MAX_FILE_SIZE:
            raise ValueError(
                f'File size ({len(file_content)} bytes) exceeds maximum '
                f'allowed size ({self.MAX_FILE_SIZE} bytes).'
            )

        # Convert to markdown
        try:
            file_io = io.BytesIO(file_content)
            file_io.name = file.filename

            result = self.markdown_processor.convert(file_io)
            if not result or not result.text_content:
                raise Exception('Conversion resulted in empty content.')

            logger.info(
                f'Successfully converted file {file.filename} to markdown'
            )

            # Get file metadata
            file_metadata = await self._get_file_metadata(file)

            result = ProcessDocumentResponse(
                markdown=result.text_content.strip(),
                metadata=file_metadata,
            )

            logger.info(f'Successfully processed document: {file.filename}')
            return result

        except Exception as e:
            logger.error(
                f'Error converting file {file.filename} to markdown: {str(e)}'
            )
            raise Exception(f'Error during conversion: {str(e)}')

    def validate_document(self, file: UploadFile) -> ValidationResponse:
        """Validate a document without processing it.

        Args:
            file (UploadFile): The uploaded file to validate.

        Returns:
            ValidationResponse: Validation result with status and details.
        """
        if not file or not file.filename:
            return ValidationResponse(
                is_valid=False,
                error='File must be provided with a valid filename.',
            )

        is_supported = self._is_file_supported(file.filename)

        error_msg = None
        if not is_supported:
            supported_formats = ', '.join(self.get_supported_extensions())
            error_msg = (
                f'Unsupported file format. '
                f'Supported formats: {supported_formats}'
            )

        return ValidationResponse(
            is_valid=is_supported,
            filename=file.filename,
            is_supported_format=is_supported,
            error=error_msg
        )

    def get_supported_extensions(self) -> List[str]:
        """Get a list of supported file extensions.

        Returns:
            List[str]: Supported file extensions.
        """
        return sorted(self.SUPPORTED_EXTENSIONS)

    # ========================================
    # Private Methods
    # ========================================

    async def _get_file_metadata(self, file: UploadFile) -> FileMetadata:
        """Extract metadata from the uploaded file.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            FileMetadata: File metadata including name, size, and type info.
        """
        # Get file size
        file_content = await file.read()
        file_size = len(file_content)

        # Reset file position
        await file.seek(0)

        return FileMetadata(
            filename=file.filename,
            size_bytes=file_size,
            size_mb=round(file_size / (1024 * 1024), 2),
            file_extension=(
                file.filename.split('.')[-1].lower()
                if '.' in file.filename else ''
            ),
            is_supported=self._is_file_supported(file.filename)
        )

    def _is_file_supported(self, filename: str) -> bool:
        """Check if the file extension is supported.

        Args:
            filename (str): The name of the file.

        Returns:
            bool: True if supported, False otherwise.
        """
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.SUPPORTED_EXTENSIONS
