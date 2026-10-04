import jwt
from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from dependencies.database import get_db
from models.user import User
from utils.security import ALGORITHM, SECRET_KEY, oauth2_scheme


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    user = db.execute(select(User).where(User.id == int(user_id))).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="User is inactive",
        )

    return user
