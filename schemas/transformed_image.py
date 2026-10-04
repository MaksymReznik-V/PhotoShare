from pydantic import BaseModel, ConfigDict


class TransformedImageResponse(BaseModel):
    id: int
    url: str
    photo_id: int

    model_config = ConfigDict(
        from_attributes=True,
    )
