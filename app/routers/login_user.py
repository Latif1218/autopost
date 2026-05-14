from fastapi import HTTPException, status, APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..database import get_db
from ..supabase_client import supabase_anon
from ..models.users_models import User
from ..authentication.users_oauth import get_current_user
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def do_login(email: str, password: str, db: Session):
    """Common login logic"""
    try:
        result = supabase_anon.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not result.user.email_confirmed_at:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your inbox."
        )

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
        "refresh_token": result.session.refresh_token,
        "token_type": "bearer",
        "expires_in": result.session.expires_in,
        "user": {
            "id": str(local_user.id),
            "email": local_user.email,
            "full_name": local_user.full_name,
            "plan": local_user.plan,
            "role": local_user.role,
            "is_verified": local_user.is_verified
        }
    }


# ✅ Swagger Authorize button এর জন্য (Form Data)
@router.post("/token", status_code=status.HTTP_200_OK)
def login_form(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    form_data: OAuth2PasswordRequestForm = Depends()
):
    return do_login(form_data.username, form_data.password, db)


# ✅ Frontend / API call এর জন্য (JSON)
@router.post("/login", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def login_json(
    request: Request,
    credentials: LoginRequest,
    db: Annotated[Session, Depends(get_db)]
):
    return do_login(credentials.email, credentials.password, db)


@router.post("/logout")
def logout():
    try:
        supabase_anon.auth.sign_out()
    except Exception:
        pass
    return {"message": "Logged out successfully"}


@router.get("/me")
def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "plan": current_user.plan,
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "is_onboarding": current_user.is_onboarding
    }


@router.get("/auth/callback")
def auth_callback(
    access_token: str = None,
    refresh_token: str = None,
    type: str = None,
    expires_in: int = None
):
    if type == "signup":
        # ✅ Email verified — login page এ redirect করো
        return {"message": "✅ Email verified successfully! You can now login."}
    elif type == "recovery":
        return {"message": "✅ Password reset verified!"}
    else:
        return {"message": "✅ Authentication successful!"}