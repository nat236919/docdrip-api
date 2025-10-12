from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configs.config import SETTINGS
from routers.v1.api_main_router import api_v1_router


# Create the app
app = FastAPI(
    title=SETTINGS.APP_TITLE,
    description=SETTINGS.APP_DESCRIPTION,
    version=SETTINGS.APP_VERSION,
    debug=SETTINGS.APP_DEBUG,
    docs_url='/docs' if SETTINGS.APP_DEBUG else None,
    redoc_url='/redoc' if SETTINGS.APP_DEBUG else None
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Register Routers
app.include_router(router=api_v1_router)
