from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


# For creating new users (API input)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


# For updating users (API input)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


# For API responses (API output)
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


# For user login (API input)
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserTokenValidation(BaseModel):
    # email: EmailStr
    access_token: str
    # token_type: str


# For login response (API output)
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    email: EmailStr


class TokenData(BaseModel):
    username: Optional[str] = None
