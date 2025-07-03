import uuid
from sqlalchemy import Column, String, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from models.base import Base

# Location model to store geographical and regional info
class Location(Base):
    __tablename__ = "locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = Column(String(100))
    region = Column(String(100))
    country = Column(String(100))
    latitude = Column(DECIMAL(9, 6))
    longitude = Column(DECIMAL(9, 6))
    timezone = Column(String(100))