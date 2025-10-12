from fastapi import APIRouter, HTTPException, UploadFile, status

from services.core_service import CoreService
from models.document_model import (
    ProcessDocumentResponse,
    SupportedFormatsResponse,
    ValidationResponse
)


core_service = CoreService()
api_document_router = APIRouter(prefix='/documents')


@api_document_router.get(
    '/supported-formats',
    status_code=status.HTTP_200_OK,
    response_model=SupportedFormatsResponse
)
async def get_supported_formats() -> SupportedFormatsResponse:
    """Get list of supported file formats for document conversion.

    Returns:
        SupportedFormatsResponse: A response containing supported file
            extensions and maximum file size.
    """
    return SupportedFormatsResponse(
        supported_formats=core_service.get_supported_extensions(),
        max_file_size_mb=core_service.MAX_FILE_SIZE / (1024 * 1024)
    )


@api_document_router.post(
    '',
    status_code=status.HTTP_200_OK,
    response_model=ProcessDocumentResponse
)
async def convert_document_to_markdown(
    file: UploadFile
) -> ProcessDocumentResponse:
    """Convert a document to markdown format.

    Args:
        file (UploadFile): The uploaded file.

    Returns:
        ProcessDocumentResponse: A response containing the converted markdown
            content and metadata about the conversion.

    Raises:
        HTTPException: If the file is not provided, empty,
            or if there is an error during conversion.
    """
    try:
        result = await core_service.process_document(file)
        return result

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error converting document: {str(e)}',
        )


@api_document_router.post(
    '/validate',
    status_code=status.HTTP_200_OK,
    response_model=ValidationResponse
)
async def validate_document(file: UploadFile) -> ValidationResponse:
    """Validate a document without processing it.

    Args:
        file (UploadFile): The uploaded file to validate.

    Returns:
        ValidationResponse: Validation result with status and details.
    """
    try:
        validation_result = core_service.validate_document(file)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Error validating document: {str(e)}',
        )
