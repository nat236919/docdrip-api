from fastapi import APIRouter

from routers.v1.documents.api_document_router import api_document_router


api_v1_router = APIRouter(prefix='/v1', tags=['v1'], dependencies=[])

api_v1_router.include_router(router=api_document_router)
