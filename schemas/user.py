from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    lastname: str = Field(min_length=1, max_length=50)
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    id: int
    username: str
    name: str
    lastname: str
    email: EmailStr
    role: str
    is_active: bool
    avatar_url: str
    registration_date: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserLogin(BaseModel):
    login: str
    password: str = Field(min_length=8)


class UserProfileResponse(BaseModel):
    username: str
    name: str
    lastname: str
    avatar_url: str
    registration_date: datetime
    photos_count: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    lastname: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )
    avatar_url: str | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool


class UserRoleUpdate(BaseModel):
    role: Literal["user", "moderator", "admin"]
