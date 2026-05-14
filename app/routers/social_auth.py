import httpx
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Optional, List
from pydantic import BaseModel
from ..authentication.users_oauth import get_current_user
from ..models.users_models import User
from ..models.businesses_model import Business
from ..models.Social_Connection_Model import SocialConnection
from ..models.generated_posts_model import GeneratedPost
from ..schemas.social_connect_request import SocialConnectRequest
from ..database import get_db
from ..config import N8N_WEBHOOK_BASE
from ..config import UPLOADPOST_API_KEY
from datetime import datetime, timezone

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
    db: Annotated[Session, Depends(get_db)]
):
    """
    User এর connected social accounts status দেখাও
    এবং social_connections table এ save/update করো
    """
 
    username = str(current_user.id)
 
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.upload-post.com/api/uploadposts/users",
                headers={
                    "Authorization": f"Apikey {UPLOADPOST_API_KEY}"
                },
                timeout=15.0
            )
 
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"UploadPost connection failed: {str(e)}"
        )
 
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch UploadPost users"
        )
 
    data = response.json()
    profiles = data.get("profiles", [])
 
    user_profile = next(
        (p for p in profiles if p.get("username") == username),
        None
    )
 
    if not user_profile:
        return {
            "connected": False,
            "platforms": [],
            "message": "No social accounts connected yet"
        }
 
    social_accounts = user_profile.get("social_accounts", {})
    connected_platforms = []
 
    for platform, details in social_accounts.items():
        if not details:
            continue
 
        # social_connections table এ check করো আছে কিনা
        existing = db.query(SocialConnection).filter(
            SocialConnection.user_id == current_user.id,
            SocialConnection.platform == platform
        ).first()
 
        if existing:
            # আগে থেকে থাকলে update করো
            existing.account_name = details.get("display_name") or details.get("handle")
            existing.account_id = details.get("handle")
            existing.is_active = True
        else:
            # নতুন হলে insert করো
            new_connection = SocialConnection(
                user_id=current_user.id,
                platform=platform,
                account_name=details.get("display_name") or details.get("handle"),
                account_id=details.get("handle"),
                is_active=True,
            )
            db.add(new_connection)
 
        connected_platforms.append({
            "platform": platform,
            "display_name": details.get("display_name"),
            "handle": details.get("handle"),
            "profile_image": details.get("social_images"),
            "reauth_required": details.get("reauth_required", False)
        })
 
    db.commit()
 
    return {
        "connected": len(connected_platforms) > 0,
        "username": username,
        "platforms": connected_platforms
    }




@router.post("/connected/trigger-schedule")
async def trigger_schedule_after_connection(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)]
):
    """Social media connection শেষ হলে n8n schedule workflow trigger করো"""
 
    # Business info নাও
    business = db.query(Business).filter(Business.user_id == current_user.id).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
 
    username = str(current_user.id)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.upload-post.com/api/uploadposts/users",
                headers={"Authorization": f"Apikey {UPLOADPOST_API_KEY}"},
                timeout=15.0
            )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"UploadPost connection failed: {str(e)}"
        )
 
    data = response.json()
    profiles = data.get("profiles", [])
    user_profile = next(
        (p for p in profiles if p.get("username") == username), None
    )
 
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No social accounts connected yet"
        )
 
    social_accounts = user_profile.get("social_accounts", {})
    platforms = [p for p, details in social_accounts.items() if details]
 
    if not platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active social platforms found"
        )
 
    plan_map = {"starter": 2, "pro": 4, "premium": 7}
    posts_per_week = plan_map.get(current_user.plan, 2)
 
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_BASE}/schedule-and-content",
                json={
                    "user_id": str(current_user.id),
                    "email": current_user.email,
                    "plan_type": current_user.plan,
                    "posts_per_week": posts_per_week,
                    "platforms": platforms,
                    "trigger_reason": "social_connected",
                    "business": {
                        "name": business.business_name,
                        "industry": business.industry,
                        "location": business.location,
                        "services": business.services,
                        "tone": business.tone,
                        "brand_color": business.brand_color,
                    }
                },
                timeout=30.0
            )
 
        if response.status_code != 200:
            logger.error(f"n8n trigger failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to trigger n8n workflow"
            )
 
        return {
            "status": "success",
            "message": "Schedule generation started",
            "plan_type": current_user.plan,
            "posts_per_week": posts_per_week,
            "platforms": platforms,
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
    




@router.get("/posts/due-now")
async def get_due_posts(db: Session = Depends(get_db)):
    """
    n8n এর জন্য — এখন publish করার সময় হয়েছে এমন posts দাও
    scheduled_at <= now AND status = 'pending'
    """
    now = datetime.now(timezone.utc)

    due_posts = db.query(GeneratedPost).filter(
        GeneratedPost.status == "pending",
        GeneratedPost.scheduled_at <= now
    ).all()

    result = []
    for post in due_posts:
        result.append({
            "post_id": str(post.id),
            "user_id": str(post.user_id),
            "content": post.content,
            "image_urls": post.media_urls,      # JSON array
            "platforms": post.platform,          # JSON array
        })

    return {"posts": result, "total": len(result)}



@router.patch("/posts/{post_id}/mark-published")
async def mark_post_published(
    post_id: str,
    db: Session = Depends(get_db)
):
    """
    n8n post করার পরে status update করবে
    """
    post = db.query(GeneratedPost).filter(
        GeneratedPost.id == post_id
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "published"
    post.published_at = datetime.now(timezone.utc)
    db.commit()

    return {"success": True, "post_id": post_id}