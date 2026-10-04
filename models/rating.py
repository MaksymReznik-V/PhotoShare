from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.photo import Photo
    from models.user import User


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("user_id", "photo_id"),
        CheckConstraint("value >= 1 AND value <= 5"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )
    user: Mapped["User"] = relationship(
        back_populates="ratings",
    )
    photo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("photos.id"),
        nullable=False,
    )
    photo: Mapped["Photo"] = relationship(
        back_populates="ratings",
    )
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
