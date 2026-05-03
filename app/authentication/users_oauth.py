# app/authentication/users_oauth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated
from ..supabase_client import supabase_admin
from ..models.users_models import User
from ..database import get_db

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: str = Depends(oauth2_schema)
) -> User:
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        response = supabase_admin.auth.get_user(token)
        supabase_user = response.user

        if not supabase_user:
            raise credentials_exception

        supabase_uid = str(supabase_user.id)

    except Exception:
        raise credentials_exception

    user = db.query(User).filter(
        User.supabase_uid == supabase_uid
    ).first()

    if not user:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.status == "suspended":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account suspended"
        )
    return current_user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def get_current_tutor_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.role != "tutor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tutor access required"
        )
    return current_user