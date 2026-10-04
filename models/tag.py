from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.photo import Photo


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
    )
    photos: Mapped[list["Photo"]] = relationship(
        secondary="photo_tags",
        back_populates="tags",
    )
