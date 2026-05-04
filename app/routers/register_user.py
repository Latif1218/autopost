from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from ..models.users_models import User
from ..schemas.users_schemas import UserCreate
from ..database import get_db
from ..supabase_client import supabase_admin, supabase_anon
from ..config import EMAIL_REGEX
import re

router = APIRouter(
    prefix="/register_user",
    tags=["Registration"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    # ১. Email format check
    if not re.match(EMAIL_REGEX, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )

    # ২. Local DB তে আছে কিনা check
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ৩. Supabase এ check
    try:
        existing_supabase = supabase_admin.auth.admin.list_users()
        for u in existing_supabase:
            if u.email == user.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
    except HTTPException:
        raise
    except Exception:
        pass

    # ৪. sign_up দিয়ে user বানাও — automatically email পাঠাবে ✅
    try:
        result = supabase_anon.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {"full_name": user.full_name}
            }
        })
        supabase_user = result.user

        if not supabase_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

    # ৫. Local DB তে save করো
    try:
        stmt = insert(User).values(
            supabase_uid=str(supabase_user.id),
            email=user.email,
            full_name=user.full_name,
            role="user",
            plan="essential",
            status="active",
            is_active=True,
            is_verified=False
        ).on_conflict_do_nothing(
            index_elements=["supabase_uid"]
        )

        db.execute(stmt)
        db.commit()

    except Exception as e:
        db.rollback()
        try:
            supabase_admin.auth.admin.delete_user(str(supabase_user.id))
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )

    return {
        "message": "Registration successful. Please check your email to verify your account."
    }