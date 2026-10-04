import io
from typing import Literal

import cloudinary.uploader
import cloudinary.utils
import qrcode
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import asc, desc, func, select
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.photo import Photo
from models.rating import Rating
from models.tag import Tag
from models.transformed_image import TransformedImage
from models.user import User
from schemas.photo import PhotoResponse, PhotoUpdate
from schemas.transformed_image import TransformedImageResponse

router = APIRouter(
    prefix="/photos",
    tags=["photos"],
)


@router.post(
    "/load",
    response_model=PhotoResponse,
    status_code=201,
)
def post_photo(
    file: UploadFile = File(...),
    description: str | None = Form(default=None),
    tags: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File must have a filename",
        )

    tag_names = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

    tag_names = list(dict.fromkeys(tag_names))

    if len(tag_names) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 tags allowed",
        )

    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="photoshare",
    )

    new_photo = Photo(
        url=upload_result["secure_url"],
        public_id=upload_result["public_id"],
        description=description,
        user_id=current_user.id,
    )

    for tag_name in tag_names:
        tag = db.execute(select(Tag).where(Tag.name == tag_name)).scalar_one_or_none()

        if tag is None:
            tag = Tag(name=tag_name)
            db.add(tag)

        new_photo.tags.append(tag)

    db.add(new_photo)
    db.commit()
    db.refresh(new_photo)

    return new_photo


@router.post(
    "/{photo_id}/transform",
    response_model=TransformedImageResponse,
    status_code=201,
)
def transform_photo(
    photo_id: int,
    width: int = 300,
    height: int = 300,
    crop: Literal["fill", "fit", "crop", "scale"] = "fill",
    effect: Literal[
        "grayscale",
        "sepia",
        "blur",
        "none",
    ] = "none",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found",
        )

    if photo.public_id is None:
        raise HTTPException(
            status_code=400,
            detail="Photo cannot be transformed",
        )

    if photo.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You cannot transform this photo",
        )

    transformation = {
        "width": width,
        "height": height,
        "crop": crop,
    }

    if effect != "none":
        transformation["effect"] = effect

    transformed_url, _ = cloudinary.utils.cloudinary_url(
        photo.public_id,
        **transformation,
    )

    transformed_image = TransformedImage(
        url=transformed_url,
        photo_id=photo.id,
    )

    db.add(transformed_image)
    db.commit()
    db.refresh(transformed_image)

    return transformed_image


@router.get(
    "/transforms/{transform_id}/qr",
)
def get_transform_qr(
    transform_id: int,
    db: Session = Depends(get_db),
):
    transformed_image = db.execute(
        select(TransformedImage).where(TransformedImage.id == transform_id)
    ).scalar_one_or_none()

    if transformed_image is None:
        raise HTTPException(
            status_code=404,
            detail="Transformed image not found",
        )

    qr_image = qrcode.make(transformed_image.url)

    buffer = io.BytesIO()
    qr_image.save(
        buffer,
        format="PNG",
    )
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png",
    )


@router.get(
    "/{photo_id}/transforms",
    response_model=list[TransformedImageResponse],
)
def get_photo_transforms(
    photo_id: int,
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found",
        )

    transformed_images = (
        db.execute(
            select(TransformedImage).where(TransformedImage.photo_id == photo_id)
        )
        .scalars()
        .all()
    )

    return transformed_images


@router.get(
    "/search/",
    response_model=list[PhotoResponse],
)
def search_photos(
    tag: str | None = None,
    description: str | None = None,
    user_id: int | None = None,
    sort_by: Literal[
        "newest",
        "oldest",
        "rating",
    ] = "newest",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Photo)

    if tag is not None:
        query = query.join(Photo.tags).where(Tag.name == tag)

    if description is not None:
        query = query.where(Photo.description.ilike(f"%{description}%"))

    if user_id is not None:
        if current_user.role not in ("moderator", "admin"):
            raise HTTPException(
                status_code=403,
                detail="Only moderator or admin can filter by user",
            )

        query = query.where(Photo.user_id == user_id)

    if sort_by == "newest":
        query = query.order_by(desc(Photo.created_at))

    elif sort_by == "oldest":
        query = query.order_by(asc(Photo.created_at))

    elif sort_by == "rating":
        query = (
            query.outerjoin(
                Rating,
                Rating.photo_id == Photo.id,
            )
            .group_by(Photo.id)
            .order_by(desc(func.avg(Rating.value)))
        )

    photos = db.execute(query).scalars().unique().all()

    return photos


@router.get(
    "/{photo_id}",
    response_model=PhotoResponse,
)
def get_photo(
    photo_id: int,
    db: Session = Depends(get_db),
):

    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    return photo


@router.put(
    "/{photo_id}",
    response_model=PhotoResponse,
)
def update_photo(
    photo_id: int,
    photo_data: PhotoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You cannot edit this photo",
        )

    photo.description = photo_data.description

    db.commit()
    db.refresh(photo)

    return photo


@router.delete(
    "/{photo_id}",
    response_model=PhotoResponse,
)
def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    if photo.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You cannot delete this photo",
        )

    db.delete(photo)
    db.commit()

    if photo.public_id is not None:
        cloudinary.uploader.destroy(photo.public_id)

    return photo
