from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from models import MatchStatus, MatchType

# Base schema for Match info with defaults
class MatchBase(BaseModel):
    match_type: MatchType = MatchType.social
    status: MatchStatus = MatchStatus.pending

# Schema for creating a new Match (requires initiator and receiver)
class MatchCreate(MatchBase):
    initiator_id: UUID
    receiver_id: UUID
    initiator_hobby_id: Optional[UUID]
    receiver_hobby_id: Optional[UUID]

# Schema for reading Match data with timestamps
class MatchRead(MatchBase):
    id: UUID
    initiator_id: UUID
    receiver_id: UUID
    initiator_hobby_id: Optional[UUID]
    receiver_hobby_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 

# TODO:
# - Add fields for match score, compatibility metrics
# - Include soft delete or archiving status
# - Support match expiration or timeout