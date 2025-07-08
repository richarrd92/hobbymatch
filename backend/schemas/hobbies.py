from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from models.enums import HobbyCategory 

# Base schema for Hobby (used internally)
class HobbyBase(BaseModel):
    name: str
    category: HobbyCategory

# Create Hobby schema (input)
class HobbyCreate(HobbyBase):
    pass

# Update Hobby schema (partial input)
class HobbyUpdate(BaseModel):
    name: Optional[str]
    category: Optional[HobbyCategory]

# Read Hobby schema (output)
class HobbyRead(HobbyBase):
    id: UUID
    created_by: Optional[UUID] 
    created_at: datetime

    class Config:
        from_attributes = True

class HobbyUpdateRequest(BaseModel):
    hobby_ids: List[UUID]


# Base: shared logic for create/read/update
class UserHobbyBase(BaseModel):
    rank: Optional[int] = Field(None, ge=1, le=3)  # Optional rank from 1 to 3

# For reading existing UserHobby entries
class UserHobbyRead(UserHobbyBase):
    id: UUID
    user_id: UUID
    hobby_id: UUID
    added_at: datetime

    class Config:
        from_attributes = True