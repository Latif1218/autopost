import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List
from pydantic import BaseModel
from ..authentication.users_oauth import get_current_user
from ..models.users_models import User
from ..schemas.social_connect_request import SocialConnectRequest
from ..database import get_db
from ..config import N8N_WEBHOOK_BASE

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/social",
    tags=["Social Media"]
)

# class SocialConnectRequest(BaseModel):
#     # whitch platforms prefer user to connect 
#     # ["facebook", "instagram", "google_business"] — any combination
#     platforms: Optional[List[str]] = ["facebook", "instagram", "google_business"]
#     redirect_url: Optional[str] = "http://localhost:8000/onboarding/style"



@router.post("/connect/test")
async def test_n8n_connection(
    req: SocialConnectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """n8n connection test করো।"""

    allowed_platforms = ["facebook", "instagram", "google_business"]
    for p in req.platforms:
        if p not in allowed_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform: {p}. Allowed: {allowed_platforms}"
            )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_BASE}/social-connect-setup",
                json={
                    "username": str(current_user.id),
                    "platforms": req.platforms,
                    "redirect_url": req.redirect_url,
                    "user_email": current_user.email,
                    "user_plan": current_user.plan
                },
                timeout=30.0
            )

        # if response.status_code != 200:
        #     logger.error(f"n8n social connect failed: {response.text}")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to generate social connect URL"
        #     )
        
        # data = response.json()
        # connect_url = data.get("connect_url")

        # if not connect_url:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="No connect URL returned"
        #     )

        return {
            "status": "success",
            "message": "Social connect request received and forwarded to n8n",
            "username": str(current_user.id),
            "platforms": req.platforms,
            "redirect_url": req.redirect_url,
            "user_email": current_user.email,
            "user_plan": str(current_user.plan),
            "n8n_status": response.status_code,
            "n8n_response": response.json() if response.status_code == 200 else None,
            "expires_in": "48 hours"
        }
        
    

    except Exception as e:
        return {"error": str(e)}





@router.post("/connect/tests")
async def test_n8n_connection(
    req: SocialConnectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Test social media connection via n8n"""
    try:
        payload = {
            "username": str(current_user.id),
            "platforms": req.platforms,
            "redirect_url": req.redirect_url or "http://localhost:3000/onboarding",
            "user_email": current_user.email,
            "user_plan": str(current_user.plan),
            "message": "Redirect user to connect_url",
            "expires_in": "48 hours"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            n8n_response = await client.post(
                f"{N8N_WEBHOOK_BASE}/social-connect-setup", 
                json=payload
            )

        return payload  

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"n8n connection failed: {str(e)}"
        )



@router.post("/connect")
async def get_social_connect_url(
    req: SocialConnectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """
    n8n trigger → Create uploadPost profile + get JWT URL
    """

    username = str(current_user.id)

    # Validate platforms
    allowed_platforms = ["facebook", "instagram", "google_business"]
    for p in req.platforms:
        if p not in allowed_platforms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid platform: {p}. Allowed: {allowed_platforms}"
            )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_BASE}/social-connect-setup",
                json={
                    "username": username,
                    "platforms": req.platforms,
                    "redirect_url": req.redirect_url,
                    "user_email": current_user.email,
                    "user_plan": current_user.plan
                },
                timeout=30.0
            )

        if response.status_code != 200:
            logger.error(f"n8n social connect failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate social connect URL"
            )

        data = response.json()
        connect_url = data.get("connect_url")

        if not connect_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No connect URL returned"
            )

        return {
            "connect_url": connect_url,
            "platforms_requested": req.platforms,
            "message": "Redirect user to connect_url",
            "expires_in": "48 hours"
        }

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="n8n timeout — try again"
        )
    except httpx.RequestError as e:
        logger.error(f"n8n request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="n8n service unavailable"
        )