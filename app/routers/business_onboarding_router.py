from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from ..models.businesses_model import Business
from ..models.businesses_model import Business
from ..models.users_models import User
from ..authentication.users_oauth import get_current_user
from ..database import get_db
from ..schemas.businesses_schema import BusinessOnboardingRequest, BusinessOnboardingResponse


router = APIRouter(
    prefix="/onboarding", 
    tags=["Onboarding"]
)

@router.post("/business", response_model=BusinessOnboardingResponse)
def onboarding_business(
    payload: BusinessOnboardingRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Business onboarding after login (JWT protected)
    """

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )

    existing = db.query(Business).filter(
        Business.user_id == current_user.id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already completed onboarding"
        )

    business = Business(
        user_id=current_user.id,
        business_name=payload.business_name,
        industry=payload.industry,
        location=payload.location,
        services=payload.services,
        tone=payload.tone,
        brand_color=payload.brand_color
    )
    db.add(business)
    db.commit()
    db.refresh(business)

    return business