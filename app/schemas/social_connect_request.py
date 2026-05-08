from pydantic import BaseModel
from typing import List, Optional

class SocialConnectRequest(BaseModel):
    platforms: List[str]
    redirect_url: Optional[str] = None