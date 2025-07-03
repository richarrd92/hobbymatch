import uuid
from sqlalchemy import Column, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from models.base import Base
from models.enums import MatchType, MatchStatus
from sqlalchemy import Enum

# Match model representing a connection between two users
class Match(Base):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # Unique match ID
    initiator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    initiator_hobby_id = Column(UUID(as_uuid=True), ForeignKey("user_hobbies.id", ondelete="SET NULL"))
    receiver_hobby_id = Column(UUID(as_uuid=True), ForeignKey("user_hobbies.id", ondelete="SET NULL"))
    match_type = Column(Enum(MatchType), default=MatchType.social)
    status = Column(Enum(MatchStatus), default=MatchStatus.pending)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    initiator = relationship("User", foreign_keys=[initiator_id], back_populates="matches_initiated")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="matches_received")
    initiator_hobby = relationship("UserHobby", foreign_keys=[initiator_hobby_id])
    receiver_hobby = relationship("UserHobby", foreign_keys=[receiver_hobby_id])
    messages = relationship("Message", cascade="all, delete", back_populates="match")
    reviews = relationship("Review", cascade="all, delete", back_populates="match")
