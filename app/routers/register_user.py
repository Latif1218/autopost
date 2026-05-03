# app/routers/register_user.py

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..models.users_models import User
from ..schemas.users_schemas import UserCreate
from ..database import get_db
from ..supabase_client import supabase_admin
from ..config import EMAIL_REGEX
import re

router = APIRouter(
    prefix="/register_user",
    tags=["Registration"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # Email format check
    if not re.match(EMAIL_REGEX, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # Already registered check
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Supabase এ user তৈরি করো
    try:
        result = supabase_admin.auth.admin.create_user({
            "email": user.email,
            "password": user.password,
            "email_confirm": False,
            "user_metadata": {"full_name": user.full_name}
        })
        supabase_user = result.user

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

    # Local DB তে save করো
    new_user = User(
        supabase_uid=str(supabase_user.id),
        email=user.email,
        full_name=user.full_name,
        is_verified=False,
        password=None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "Registration successful. Please check your email to verify your account."
    }