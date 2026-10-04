from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.comment import Comment
    from models.rating import Rating
    from models.tag import Tag
    from models.transformed_image import TransformedImage
    from models.user import User


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    url: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    public_id: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="photos",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="photo_tags",
        back_populates="photos",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="photo",
    )
    transformed_images: Mapped[list["TransformedImage"]] = relationship(
        back_populates="photo",
    )
    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="photo",
    )
