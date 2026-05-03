from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum



class IndustryType(str, Enum):
    PHONE_TABLET_REPAIR = "Phone & Tablet Repair"
    BARBERSHOP_HAIR_SALON = "Barbershop / Hair Salon"
    NAIL_SALON = "Nail Salon"
    RESTAURANT_CAFE = "Restaurant / Café"
    AUTO_DETAILING_MECHANIC = "Auto Detailing / Mechanic"
    CLEANING_SERVICE = "Cleaning Service"
    PET_GROOMING = "Pet Grooming"
    TATTOO_STUDIO = "Tattoo Studio"
    PLUMBER_ELECTRICIAN = "Plumber / Electrician"
    GYM_FITNESS = "Gym / Fitness"
    OTHER = "Other"


class BrandTone(str, Enum):
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    BOLD_ENERGETIC = "Bold & Energetic"
    LUXURY = "Luxury"

class BrandColor(str, Enum):
    ORANGE = "#FF5733"
    BLUE = "#3B82F6"
    PURPLE = "#8B5CF6"
    GREEN = "#10B981"
    YELLOW = "#F59E0B"
    RED = "#EF4444"
    PINK = "#EC4899"
    DARK = "#374151"



class BusinessOnboardingRequest(BaseModel):
    business_name: Optional[str] = None
    industry: Optional[IndustryType] = None
    location: Optional[str] = None
    services: Optional[str] = None
    tone: Optional[BrandTone] = None  
    brand_color: Optional[BrandColor] = None




class BusinessOnboardingResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    business_name: Optional[str]
    industry: Optional[IndustryType]
    location: Optional[str]
    services: Optional[str]
    tone: Optional[BrandTone]          
    brand_color: Optional[BrandColor] 
    created_at: datetime

    class Config:
        from_attributes = True