# app/routers/login_user.py

from fastapi import HTTPException, status, APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..supabase_client import supabase_anon
from ..models.users_models import User
from ..schemas.users_schemas import UserResponse
from ..authentication.users_oauth import get_current_user
from pydantic import BaseModel, EmailStr

router = APIRouter(
    prefix="",
    tags=["Authentication"]
)

limiter = Limiter(key_func=get_remote_address)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/token", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def login(
    request: Request,
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    # Supabase দিয়ে login
    try:
        result = supabase_anon.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Email verified কিনা check
    if not result.user.email_confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox."
        )

    # Local DB থেকে user আনো
    local_user = db.query(User).filter(
        User.supabase_uid == str(result.user.id)
    ).first()

    if not local_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "access_token": result.session.access_token,
        "token_type": "bearer",
        "user": {
            "id": str(local_user.id),
            "email": local_user.email,
            "plan": local_user.plan,
            "role": local_user.role
        }
    }


@router.post("/logout")
def logout():
    try:
        supabase_anon.auth.sign_out()
    except Exception:
        pass
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user