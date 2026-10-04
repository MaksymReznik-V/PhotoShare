from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    value: int = Field(
        ge=1,
        le=5,
    )


class RatingResponse(BaseModel):
    id: int
    user_id: int
    photo_id: int
    value: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class PhotoRatingResponse(BaseModel):
    photo_id: int
    average_rating: float
    ratings_count: int
