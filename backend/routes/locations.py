from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geopy.geocoders import Nominatim
from models import Location
from schemas import LocationResolveRequest, LocationRead
from database import get_db
from utils.current_user import blur_and_round
from timezonefinder import TimezoneFinder


router = APIRouter(prefix="/locations", tags=["Locations"])

# List all saved locations
@router.get("/")
async def list_locations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Location))
    locations = result.scalars().all()
    return locations

# Reverse geocode coordinates and return or create a Location
@router.post("/resolve", response_model=LocationRead)
async def resolve_location(
    loc_req: LocationResolveRequest, db: AsyncSession = Depends(get_db)
):

    latitude = blur_and_round(loc_req.latitude)
    longitude = blur_and_round(loc_req.longitude)

    # Use geopy to resolve the location
    geolocator = Nominatim(user_agent="hobbymatch-app")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    
    # If no location is found, raise an error
    if not location:
        raise HTTPException(status_code=400, detail="Unable to resolve location")
    
    # Extract components from geocoded data
    addr = location.raw.get("address", {})
    city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
    region = addr.get("state") or "Unknown"
    country = addr.get("country") or "Unknown"

    # Determine timezone
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=latitude, lng=longitude) or "Unknown"

    # Check if location already exists
    query = select(Location).where(
        Location.city == city,
        Location.region == region,
        Location.country == country,
        Location.latitude == latitude,
        Location.longitude == longitude
    )

    # If location exists, return it
    result = await db.execute(query)
    loc = result.scalars().first()
    if loc:
        return loc

    # Else, create new location
    new_loc = Location(
        city=city,
        region=region,
        country=country,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )

    # Add new location to database
    db.add(new_loc)
    await db.commit()
    await db.refresh(new_loc)
    return new_loc # Return new location


# TODO: Implement additional Location-related endpoints:
# - GET /locations/{id}       : Retrieve a location by its ID
# - POST /locations           : Create a new location manually
# - PATCH /locations/{id}     : Update existing location data
# - DELETE /locations/{id}    : Delete a location (if allowed)
# - GET /locations/search     : Search locations by city, region, or country
# - GET /locations/nearby     : Find locations near given coordinates
# - Integration endpoints for linking locations with users, events, hobbies, etc.