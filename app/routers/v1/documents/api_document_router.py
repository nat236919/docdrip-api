from fastapi import APIRouter, HTTPException, UploadFile, status

from services.core_service import CoreService


core_service = CoreService()
api_document_router = APIRouter(prefix='/documents')


@api_document_router.get('/supported-formats', status_code=status.HTTP_200_OK)
async def get_supported_formats() -> dict:
    """Get list of supported file formats for document conversion.

    Returns:
        dict: A dictionary containing supported file extensions.
    """
    return {
        'supported_formats': core_service.get_supported_extensions(),
        'max_file_size_mb': core_service.MAX_FILE_SIZE / (1024 * 1024)
    }


@api_document_router.post('', status_code=status.HTTP_200_OK)
async def convert_document_to_markdown(file: UploadFile) -> dict:
    """Convert a document to markdown format.

    Args:
        file (UploadFile): The uploaded file.

    Returns:
        dict: A dictionary containing the converted markdown content and
            metadata about the conversion.

    Raises:
        HTTPException: If the file is not provided, empty,
            or if there is an error during conversion.
    """
    try:
        # Pre-validate file support
        if not core_service.is_file_supported(file.filename):
            supported = core_service.get_supported_extensions()
            supported_str = ", ".join(supported)
            raise ValueError(
                f'Unsupported file format. Supported formats: {supported_str}'
            )

        markdown_content = await core_service.convert_file_to_markdown(file)
        return {
            'markdown': markdown_content,
            'filename': file.filename,
            'supported_formats': core_service.get_supported_extensions()
        }

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
