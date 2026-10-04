from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    photo_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )
