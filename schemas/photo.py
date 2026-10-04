from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.tags import TagResponse


class PhotoCreate(BaseModel):
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PhotoUpdate(BaseModel):
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PhotoResponse(BaseModel):
    id: int
    url: str
    description: str | None
    tags: list[TagResponse]
    created_at: datetime
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )
