from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from configs.config import SETTINGS


class AuthService:
    """Auth Services to be used by the API."""

    def __init__(self):
        self.api_key = SETTINGS.APP_SECRET_KEY

    def validate_api_key(
        self,
        api_key_header: str = Security(APIKeyHeader(name='X-API-Key'))
    ) -> bool:
        """Validate the API Key in Header.

        Args:
            token (str): The API token.

        Returns:
            bool: True if valid, False otherwise.

        Raises:
            HTTPException: If the API key is invalid or missing.
        """
        if not api_key_header or str(api_key_header) != str(self.api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Unauthorized'
            )

        return True
