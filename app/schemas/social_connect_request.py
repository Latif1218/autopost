from pydantic import BaseModel, ConfigDict, field_validator

from typing import Any, List, Optional
from datetime import datetime
from uuid import UUID

class SocialConnectRequest(BaseModel):
    platforms: List[str]
    redirect_url: Optional[str] = None



class GeneratedPostPendingResponse(BaseModel):
    id: UUID
    user_id: UUID
    platform: Optional[str] = None
    content: Optional[str] = None
    media_urls: List[str] = []
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    queue_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("media_urls", mode="before")
    @classmethod
    def normalize_media_urls(cls, value: Any):
        if value is None:
            return []

        if isinstance(value, list):
            return [item for item in value if item]

        if isinstance(value, str):
            return [value] if value else []

        return []