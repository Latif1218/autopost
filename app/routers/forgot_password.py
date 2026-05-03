# app/routers/forgot_password.py

from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
from ..database import get_db
from ..supabase_client import supabase_admin
from ..models.users_models import User
from ..authentication.users_oauth import get_current_user
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(
    prefix="/forgot",
    tags=["Forgot Password"]
)

limiter = Limiter(key_func=get_remote_address)


class ForgotRequest(BaseModel):
    email: EmailStr


class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)


@router.post("/forgot_pass", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
def forgot_password(
    request: Request,
    payload: ForgotRequest
):
    try:
        supabase_admin.auth.reset_password_email(
            payload.email,
            options={
                "redirect_to": "https://yourdomain.com/reset-password"
            }
        )
    except Exception:
        pass  

    return {
        "status": "success",
        "message": "If this email exists, a reset link has been sent."
    }


@router.put("/update_password", status_code=status.HTTP_200_OK)
def update_password(
    payload: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        supabase_admin.auth.admin.update_user_by_id(
            current_user.supabase_uid,
            {"password": payload.new_password}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password update failed"
        )

    current_user.updated_at = datetime.utcnow()
    db.commit()

    return {
        "status": "success",
        "message": "Password updated successfully"
    }