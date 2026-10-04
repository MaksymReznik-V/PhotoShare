from sqlalchemy import Column, ForeignKey, Integer, Table

from database import Base

photo_tags = Table(
    "photo_tags",
    Base.metadata,
    Column(
        "photo_id",
        Integer,
        ForeignKey("photos.id"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("tags.id"),
        primary_key=True,
    ),
)
