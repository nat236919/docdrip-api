from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.v1.api_main_router import api_v1_router


# Create the app
app = FastAPI()

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
