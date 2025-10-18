from fastapi import APIRouter, Depends

from services.core_service import CoreService
from routers.v1.documents.api_document_router import api_document_router
from models.main_router_model import OperationalStatus


api_v1_router = APIRouter(
    prefix="/v1",
    tags=["v1"],
    dependencies=[
        # TODO: Incldue this when tests are fixed
        # Depends(CoreService().auth_service.validate_api_key)
    ],
)

api_v1_router.include_router(router=api_document_router)


@api_v1_router.get('')
async def get_operational_status() -> OperationalStatus:
    """Check if the API v1 router is operational.

    Returns:
        OperationalStatus: The operational status of the API v1 router.
    """
    return OperationalStatus(operational=True)
