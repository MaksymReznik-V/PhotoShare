from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.photo import Photo
from models.rating import Rating
from models.user import User
from schemas.rating import (
    PhotoRatingResponse,
    RatingCreate,
    RatingResponse,
)

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"],
)


@router.post(
    "/photos/{photo_id}",
    response_model=RatingResponse,
    status_code=201,
)
def create_rating(
    photo_id: int,
    rating_data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found",
        )

    if photo.user_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot rate your own photo",
        )

    existing_rating = db.execute(
        select(Rating).where(
            Rating.user_id == current_user.id,
            Rating.photo_id == photo_id,
        )
    ).scalar_one_or_none()

    if existing_rating is not None:
        raise HTTPException(
            status_code=409,
            detail="You have already rated this photo",
        )

    new_rating = Rating(
        user_id=current_user.id,
        photo_id=photo_id,
        value=rating_data.value,
    )

    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)

    return new_rating


@router.get(
    "/photos/{photo_id}",
    response_model=PhotoRatingResponse,
)
def get_photo_rating(
    photo_id: int,
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found",
        )

    average_rating, ratings_count = db.execute(
        select(
            func.avg(Rating.value),
            func.count(Rating.id),
        ).where(Rating.photo_id == photo_id)
    ).one()

    return PhotoRatingResponse(
        photo_id=photo_id,
        average_rating=float(average_rating or 0),
        ratings_count=ratings_count,
    )


@router.delete(
    "/{rating_id}",
    response_model=RatingResponse,
)
def delete_rating(
    rating_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("moderator", "admin"):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete ratings",
        )

    rating = db.execute(
        select(Rating).where(Rating.id == rating_id)
    ).scalar_one_or_none()

    if rating is None:
        raise HTTPException(
            status_code=404,
            detail="Rating not found",
        )

    db.delete(rating)
    db.commit()

    return rating


@router.get(
    "/",
    response_model=list[RatingResponse],
)
def get_ratings(
    photo_id: int | None = None,
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in ("moderator", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only moderator or admin can view ratings",
        )

    query = select(Rating)

    if photo_id is not None:
        query = query.where(Rating.photo_id == photo_id)

    if user_id is not None:
        query = query.where(Rating.user_id == user_id)

    ratings = db.execute(query.order_by(Rating.id)).scalars().all()

    return ratings
