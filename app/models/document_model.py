from typing import List, Optional
from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    """Model for file metadata information."""

    filename: str = Field(..., description='Name of the uploaded file')
    size_bytes: int = Field(..., description='File size in bytes')
    size_mb: float = Field(..., description='File size in megabytes')
    file_extension: str = Field(..., description='File extension (lowercase)')
    is_supported: bool = Field(
        ..., description='Whether the file format is supported'
    )


class ProcessDocumentResponse(BaseModel):
    """Model for document processing response."""

    markdown: str = Field(..., description='Converted markdown content')
    metadata: FileMetadata = Field(..., description='File metadata')


class ValidationResponse(BaseModel):
    """Model for document validation response."""

    is_valid: bool = Field(..., description='Whether the file is valid')
    filename: Optional[str] = Field(
        None, description='Name of the file being validated'
    )
    is_supported_format: Optional[bool] = Field(
        None, description='Whether the format is supported'
    )
    error: Optional[str] = Field(
        None, description='Error message if validation failed'
    )


class SupportedFormatsResponse(BaseModel):
    """Model for supported formats response."""

    supported_formats: List[str] = Field(
        ..., description='List of supported file extensions'
    )
    max_file_size_mb: float = Field(
        ..., description='Maximum allowed file size in MB'
    )
