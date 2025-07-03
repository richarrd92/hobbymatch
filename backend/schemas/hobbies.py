from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from models import HobbyCategory

# Base schema for Hobby data
class HobbyBase(BaseModel):
    name: str
    category: HobbyCategory
    created_by: Optional[UUID]

# Schema for creating a new Hobby
class HobbyCreate(HobbyBase):
    pass # Inherits all fields from HobbyBase

# Schema for reading Hobby data
class HobbyRead(HobbyBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 

# TODO:
# - Track creator user ID if needed
# - Add fields like updated_at, description, or popularity metrics in future
