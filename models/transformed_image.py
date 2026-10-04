from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

if TYPE_CHECKING:
    from models.photo import Photo


class TransformedImage(Base):
    __tablename__ = "transformed_images"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )
    photo_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("photos.id"),
        nullable=False,
    )
    photo: Mapped["Photo"] = relationship(
        back_populates="transformed_images",
    )
