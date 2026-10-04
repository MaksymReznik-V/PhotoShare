from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.photo import Photo
from models.user import User
from schemas.user import (
    UserCreate,
    UserProfileResponse,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)
from utils.security import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    existing_user = db.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists",
        )

    existing_user = db.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User with this username already exists",
        )

    hashed_password = hash_password(user.password)

    first_user = db.execute(select(User.id).limit(1)).scalar_one_or_none()

    role = "admin" if first_user is None else "user"

    new_user = User(
        username=user.username,
        name=user.name,
        lastname=user.lastname,
        email=user.email,
        password_hash=hashed_password,
        role=role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def user_login(
    credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = db.execute(
        select(User).where(
            or_(
                User.username == credentials.username,
                User.email == credentials.username,
            )
        )
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid login or password",
        )

    if not verify_password(
        credentials.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid login or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get(
    "/{username}",
    response_model=UserProfileResponse,
)
def get_user_profile(
    username: str,
    db: Session = Depends(get_db),
):
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    photos_count = db.execute(
        select(func.count(Photo.id)).where(Photo.user_id == user.id)
    ).scalar_one()

    return UserProfileResponse(
        username=user.username,
        name=user.name,
        lastname=user.lastname,
        avatar_url=user.avatar_url,
        registration_date=user.registration_date,
        photos_count=photos_count,
    )


@router.put(
    "/me",
    response_model=UserResponse,
)
def update_me(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user_data.name is not None:
        current_user.name = user_data.name

    if user_data.lastname is not None:
        current_user.lastname = user_data.lastname

    if user_data.avatar_url is not None:
        current_user.avatar_url = user_data.avatar_url

    new_username = user_data.username

    if new_username is not None and new_username != current_user.username:
        existing_user = db.execute(
            select(User).where(User.username == new_username)
        ).scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=409,
                detail="Username already exists",
            )

        current_user.username = str(new_username)

    db.commit()
    db.refresh(current_user)

    return current_user


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can change user status",
        )

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.is_active = status_data.is_active

    db.commit()
    db.refresh(user)

    return user


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
)
def update_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admin can change user role",
        )

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user.role = role_data.role

    db.commit()
    db.refresh(user)

    return user
