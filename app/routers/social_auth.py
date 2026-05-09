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

@router.post("/connect/test")
async def test_n8n_connection(
    req: SocialConnectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Test social media connection via n8n"""

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

        if response.status_code != 200:
            logger.error(f"n8n social connect failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate social connect URL"
            )
        
        data = response.json()
        if not data or not isinstance(data, list):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid response from n8n"
            )
        
        result = data[0]

        connect_url = result.get("access_url")

        if not connect_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No connect URL returned"
            )

        return {
            "n8n_status": response.status_code,
            "status": "success",
            "message": "Social connect request received and forwarded to n8n",
            "success": result.get("success", False),
            "connect_url": connect_url,
            "duration": result.get("duration"),
            "platforms_requested": req.platforms,
            "message": "Redirect user to connect_url"
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




@router.get("/status")
async def get_social_status(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """User এর connected social media accounts দেখাও।"""
    from ..config import UPLOADPOST_API_KEY

    username = str(current_user.id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.upload-post.com/api/uploadposts/users",
            headers={"Authorization": f"Apikey {UPLOADPOST_API_KEY}"},
            timeout=15.0
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch social status"
        )

    users = response.json()

    user_profile = next(
        (
            u for u in users
            if isinstance(u, dict) and u.get("username") == username
        ),
        None
    )

    if not user_profile:
        return {
            "connected": False,
            "platforms": [],
            "message": "No social accounts connected yet"
        }

    return {
        "connected": True,
        "username": username,
        "platforms": user_profile.get("connected_accounts", []),
    }
