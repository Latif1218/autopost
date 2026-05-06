from pydantic import BaseModel, EmailStr, Field, field_validator

class ForgotPasswoedRequest(BaseModel):
    email: EmailStr
    model_config = {
        "extra" : "forbid"
    }


class PasswordUpdate(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128, description="password must be between 8 to 128 characters")
    model_config = {
        "extra" : "forbid"
    }


class PasswordResetRequest(BaseModel):       
    new_password: str = Field(..., min_length=8, max_length=128, description="password must be between 8 to 128 characters")
    access_token: str 
    refresh_token: str = None