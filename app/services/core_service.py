import io
import logging
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from markitdown import MarkItDown


logger = logging.getLogger(__name__)


class CoreService:
    """Service for handling document conversion operations."""

    # Maximum file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf', '.docx', '.doc', '.txt', '.md', '.html', '.htm',
        '.xlsx', '.xls', '.pptx', '.ppt', '.rtf'
    }

    def __init__(self):
        self.markdown_processor = MarkItDown()

    async def convert_file_to_markdown(self, file: UploadFile) -> str:
        """Convert an uploaded file to markdown format.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            str: The converted markdown content.

        Raises:
            ValueError: If the file is not provided, empty, too large,
                or unsupported format.
            Exception: If there is an error during conversion.
        """
        if not file:
            raise ValueError('File must be provided.')

        if not file.filename:
            raise ValueError('File must have a filename.')

        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.SUPPORTED_EXTENSIONS:
            supported_formats = ", ".join(sorted(self.SUPPORTED_EXTENSIONS))
            raise ValueError(
                f'Unsupported file format: {file_extension}. '
                f'Supported formats: {supported_formats}'
            )

        # Read file content
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading file {file.filename}: {str(e)}")
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
            # Set filename for MarkItDown to help with format detection
            file_io.name = file.filename

            result = self.markdown_processor.convert(file_io)

            if not result or not result.text_content:
                raise Exception('Conversion resulted in empty content.')

            logger.info(
                f"Successfully converted file {file.filename} to markdown"
            )
            return result.text_content.strip()

        except Exception as e:
            logger.error(
                f"Error converting file {file.filename} to markdown: {str(e)}"
            )
            raise Exception(f'Error during conversion: {str(e)}')

    def get_supported_extensions(self) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            list[str]: List of supported file extensions.
        """
        return sorted(list(self.SUPPORTED_EXTENSIONS))

    def is_file_supported(self, filename: Optional[str]) -> bool:
        """Check if a file is supported based on its extension.

        Args:
            filename (Optional[str]): The filename to check.

        Returns:
            bool: True if the file is supported, False otherwise.
        """
        if not filename:
            return False

        file_extension = Path(filename).suffix.lower()
        return file_extension in self.SUPPORTED_EXTENSIONS
