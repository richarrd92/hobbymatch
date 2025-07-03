from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

# Base schema for user's hobby with optional rank (1-3)
class UserHobbyBase(BaseModel):
    rank: Optional[int] = Field(None, ge=1, le=3)

# Schema for creating a UserHobby relation (requires user and hobby IDs)
class UserHobbyCreate(UserHobbyBase):
    user_id: UUID
    hobby_id: UUID

# Schema for reading UserHobby data including timestamps
class UserHobbyRead(UserHobbyBase):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    added_at: datetime

    class Config:
        from_attributes = True 

# TODO:
# - Add support for notes or comments on hobbies
# - Track last_updated timestamp if hobbies can be re-ranked