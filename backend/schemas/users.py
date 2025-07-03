from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from schemas.locations import LocationRead
from models import UserRole

# Base user data schema
class UserBase(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int]
    bio: Optional[str]
    profile_pic_url: Optional[str]
    location_id: Optional[UUID]
    role: Optional[UserRole] = UserRole.user
    is_verified: Optional[bool] = False
    verification_method: Optional[str]
    is_private: Optional[bool] = False

# Schema for creating a new user (firebase_uid required)
class UserCreate(UserBase):
    firebase_uid: str 

# Schema for reading user data with metadata and location
class UserRead(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    location: Optional[LocationRead]

    class Config:
        from_attributes = True 

# Schema for user profile update with photo upload support
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    is_private: Optional[bool] = None
    location_id: Optional[UUID] = None
    photos_base64: Optional[List[str]] = Field(default_factory=list)
    photos_urls: Optional[List[str]] = Field(default_factory=list)
    profile_pic_base64: Optional[str] = None

# TODO:
# - Add fields to UserRead for hobbies, photos, and matches relationships
# - Support multi-photo upload and storage in UserProfileUpdate
# - Add validation for photo formats and sizes
# - Add optional fields like social links, status messages, or user preferences