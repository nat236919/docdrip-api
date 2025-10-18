from pydantic import BaseModel, Field


class OperationalStatus(BaseModel):
    """Model for main router response."""

    operational: bool = Field(
        ..., description="Indicates if the API router is operational"
    )
