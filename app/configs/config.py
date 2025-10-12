
import os
from typing import Union
from dotenv import load_dotenv

from pydantic import BaseModel

load_dotenv(
    verbose=True,
    override=True
)


class Config(BaseModel):
    """Settings for the application."""

    # APP settings
    _app_debug: Union[bool, str] = os.getenv('APP_DEBUG', 'False')

    APP_TITLE: str = 'DocDrip API'
    APP_DESCRIPTION: str = 'API for converting documents to markdown format'

    APP_VERSION: str = os.getenv('APP_VERSION')
    APP_HOST: str = os.getenv('APP_HOST')
    APP_PORT: str = os.getenv('APP_PORT')
    APP_SECRET_KEY: str = os.getenv('APP_SECRET_KEY')

    @property
    def APP_DEBUG(self) -> bool:
        if isinstance(self._app_debug, str):
            true_str_values = ('true', '1', 't', 'y', 'yes')
            return self._app_debug.lower().strip() in true_str_values
        return self._app_debug


SETTINGS = Config()
