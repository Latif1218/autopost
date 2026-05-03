from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from enum import Enum
from app.models.users_models import UserRole, UserPlan, UserStatus


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE
    


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Minimum 8 characters")


class UserResponse(BaseModel):
    id: UUID
    full_name: Optional[str] = None
    email: EmailStr
    role: UserRole
    plan: UserPlan
    status: UserStatus
    created_at: datetime
    updated_at: Optional[datetime]

    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "role": "user",
                "plan": "premium",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }
    } 



class VerifyOTP(BaseModel):
    email: str
    otp: str



class TokenData(BaseModel):
    id : Optional[UUID] = None
    
    

class UserToken(BaseModel):
    access_token : str
    token_type : str

    model_config = {
        "from_attributes": True
    }    
