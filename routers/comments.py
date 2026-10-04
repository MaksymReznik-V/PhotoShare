from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.comment import Comment
from models.photo import Photo
from models.user import User
from schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)

router = APIRouter(
    prefix="/comments",
    tags=["comments"],
)


@router.post(
    "/photos/{photo_id}",
    response_model=CommentResponse,
    status_code=201,
)
def create_comment(
    photo_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    photo = db.execute(select(Photo).where(Photo.id == photo_id)).scalar_one_or_none()

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found",
        )

    new_comment = Comment(
        text=comment_data.text,
        user_id=current_user.id,
        photo_id=photo_id,
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.execute(
        select(Comment).where(Comment.id == comment_id)
    ).scalar_one_or_none()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot edit this comment",
        )

    comment.text = comment_data.text

    db.commit()
    db.refresh(comment)

    return comment


@router.delete(
    "/{comment_id}",
    response_model=CommentResponse,
)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.execute(
        select(Comment).where(Comment.id == comment_id)
    ).scalar_one_or_none()

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if current_user.role not in ("moderator", "admin"):
        raise HTTPException(
            status_code=403,
            detail="You cannot delete comments",
        )

    db.delete(comment)
    db.commit()

    return comment
