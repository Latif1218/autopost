# app/routers/forgot_password.py

from fastapi import APIRouter, HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime
from ..database import get_db
from ..supabase_client import supabase_admin, supabase_anon
from ..models.users_models import User
from ..schemas.forgot_password_schema import ForgotPasswoedRequest, PasswordUpdate, PasswordResetRequest
from ..authentication.users_oauth import get_current_user
from pydantic import BaseModel, EmailStr, Field

from app import supabase_client

router = APIRouter(
    prefix="/forgot",
    tags=["Forgot Password"]
)

limiter = Limiter(key_func=get_remote_address)


@router.post("/forgot_pass", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
def forgot_password(
    request: Request,
    payload: ForgotPasswoedRequest
):
    try:
        supabase_anon.auth.reset_password_email(
            payload.email,
            options={
                "redirect_to": "http://localhost:8000/reset-password"
            }
        )
    except Exception:
        pass  

    return {
        "status": "success",
        "message": "If this email exists, a reset link has been sent."
    }



@router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_with_token(
    payload: PasswordResetRequest
):
    try:
        if payload.refresh_token:
            supabase_anon.auth.set_session(
                access_token=payload.access_token,
                refresh_token=payload.refresh_token
            )
        else:
            supabase_anon.auth.verify_otp(
                token=payload.access_token,
                type="recovery"
            )

        supabase_anon.auth.update_user(
            attributes={"password": payload.new_password}
        )

        return {
            "status": "success",
            "message": "Password reset successfully."
        }

    except Exception as e:
        print("Reset Password Error:", str(e))  
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset link. Please request a new one."
        )




@router.put("/update_password", status_code=status.HTTP_200_OK)
def update_password(
    payload: PasswordUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        supabase_anon.auth.update_user(
            attributes={"password": payload.new_password}
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