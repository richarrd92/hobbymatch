from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# Base schema for location data
class LocationBase(BaseModel):
    city: Optional[str]
    region: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timezone: Optional[str]

# Schema for creating a location (all fields required)
class LocationCreate(LocationBase):
    city: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str

# Schema for reading location data (includes ID)
class LocationRead(LocationBase):
    id: UUID

    class Config:
        from_attributes = True 

# Request schema for resolving location from coordinates
class LocationResolveRequest(BaseModel):
    latitude: float
    longitude: float

# TODO:
# - Add fields for postal codes, landmarks, or more granular address components if needed
# - Support batch geolocation resolving
# - Add timezone resolution improvements or caching