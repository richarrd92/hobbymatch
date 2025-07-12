from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from geopy.geocoders import Nominatim 
from models import Location
from schemas import LocationResolveRequest, LocationRead
from database import get_db
from utils.current_user import blur_and_round
from timezonefinder import TimezoneFinder
from logger import logger

# Define API router for location endpoints
router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("", response_model=list[LocationRead])
async def list_locations(db: AsyncSession = Depends(get_db)):
    """
    Fetch all saved locations from the database.

    Parameters:
    - db (AsyncSession): DB session.

    Returns:
    - List[LocationRead]: All location records.
    """

    try:
        # Fetch all locations
        result = await db.execute(select(Location))
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching locations")

@router.post("/resolve", response_model=LocationRead, status_code=status.HTTP_201_CREATED)
async def resolve_location(
    loc_req: LocationResolveRequest, db: AsyncSession = Depends(get_db)
):
    """
    Reverse geocode coordinates, check if location exists, and return or create it.

    Parameters:
    - loc_req (LocationResolveRequest): Latitude and longitude input.
    - db (AsyncSession): DB session.

    Returns:
    - LocationRead: Existing or newly created location.

    Raises:
    - HTTP 400 if coordinates cannot be resolved.
    """

    # Blur and round coordinates for privacy
    latitude = blur_and_round(loc_req.latitude)
    longitude = blur_and_round(loc_req.longitude)

    # Reverse geocode using Nominatim
    try:
        geolocator = Nominatim(user_agent="hobbymatch-app")
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        raise HTTPException(status_code=400, detail="Error resolving coordinates")

    # If no location is found, raise an error
    if not location:
        raise HTTPException(status_code=400, detail="Unable to resolve location")
    
    # Extract components from geocoded data
    addr = location.raw.get("address", {})
    city = addr.get("city") or addr.get("town") or addr.get("village") or "Unknown"
    region = addr.get("state") or "Unknown"
    country = addr.get("country") or "Unknown"

    # Determine timezone using TimezoneFinder
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=latitude, lng=longitude) or "Unknown"

    # Check if location already exists in DB
    query = select(Location).where(
        Location.city == city,
        Location.region == region,
        Location.country == country,
        Location.latitude == latitude,
        Location.longitude == longitude
    )

    # If location exists, return it
    result = await db.execute(query)
    existing_location = result.scalars().first()
    if existing_location:
        return existing_location

    # Else, Create new location entry
    new_location = Location(
        city=city,
        region=region,
        country=country,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone
    )

    # Add new location to database
    db.add(new_location)
    await db.commit()
    await db.refresh(new_location)
    return new_location # Return new location


# TODO: Implement additional Location-related endpoints:
# - GET /locations/{id}       : Retrieve a location by its ID
# - POST /locations           : Create a new location manually
# - PATCH /locations/{id}     : Update existing location data
# - DELETE /locations/{id}    : Delete a location (if allowed)
# - GET /locations/search     : Search locations by city, region, or country
# - GET /locations/nearby     : Find locations near given coordinates
# - Integration endpoints for linking locations with users, events, hobbies, etc.