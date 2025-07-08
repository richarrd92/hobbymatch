from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, delete, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import base64
from models import User, Location, UserRole, UserHobby, Hobby
from schemas import UserRead, UserProfileUpdate
from database import get_db
from logger import logger
from utils.admin import require_admin
from utils.cloudinary import upload_photo_to_cloudinary
from utils.current_user import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# TODO: Change size if needed
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024 # 5MB

# Allowed fields for sorting
ALLOWED_SORT_FIELDS = {
    "name", "email", "age", "role",
    "is_verified", "is_private", "created_at", "updated_at"
}

# Allowed fields for user profile update
ALLOWED_PROFILE_UPDATE_FIELDS = [
    "name", "age", "bio", "profile_pic_url", "location_id", "is_private"
]


# Retrieve a paginated list of users with optional filtering, searching, and sorting.
@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = Query(10, le=100),  # Limit to a maximum of 100
    search: str | None = None,
    name: str | None = None,
    email: str | None = None,
    role: str | None = None,
    is_verified: bool | None = None,
    is_private: bool | None = None,
    min_age: int | None = None,
    max_age: int | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_admin(current_user)  # Ensure the user is an Admin

    try:
        # Base query with common relationships
        query = select(User).options(
            selectinload(User.location),
            selectinload(User.photos),
            # TODO: Add more relationships
            # Add selectinload(User.hobbies), 
            # selectinload(User.matches_initiated)
        )

        # Global search across name/email
        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(term),
                    User.email.ilike(term)
                    # TODO: Add more field
                )
            )

        # Optional filters
        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(User.email.ilike(f"%{email}%"))
        if role:
            query = query.filter(User.role == UserRole(role))
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        if is_private is not None:
            query = query.filter(User.is_private == is_private)
        if min_age is not None:
            query = query.filter(User.age >= min_age)
        if max_age is not None:
            query = query.filter(User.age <= max_age)

        # Validate sort field
        if sort_by not in ALLOWED_SORT_FIELDS:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")
        sort_column = getattr(User, sort_by)
        query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

        # Pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        users = result.scalars().all()
        logger.info(f"Admin {current_user.email} retrieved {len(users)} users")
        return users

    except HTTPException:
        raise # Re-raise known HTTP errors
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Get the current authenticated user's profile
@router.get("/me", response_model=UserRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # Query user with related location
        result = await db.execute(
            select(User)
            .options(selectinload(User.location))
            .filter(User.id == current_user.id)
        )
        user = result.scalar_one_or_none()

        # Check if user exists
        if not user:
            logger.error(f"User not found for {current_user.email}")
            raise HTTPException(status_code=404, detail="User not found")
        
        logger.info(f"Loaded profile for {current_user.email}")
        return user # Return the user
    
    except HTTPException:
        raise # Re-raise known HTTP errors
    except Exception as e:
        logger.error(f"Failed to load user profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load profile")

# Update the current user's profile with optional fields and profile picture upload
@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updates = update.dict(exclude_unset=True)

    # Validate location if provided
    if "location_id" in updates:
        loc_result = await db.execute(select(Location).filter(Location.id == updates["location_id"]))
        if not loc_result.scalars().first():
            logger.error(f"Invalid location_id: {updates['location_id']}")
            raise HTTPException(status_code=400, detail="Invalid location_id")

    # Handle profile picture upload from base64
    if "profile_pic_base64" in updates:
        b64data = updates.pop("profile_pic_base64")
        if not b64data or len(b64data) < 100:
            logger.error(f"Invalid profile picture data for user {current_user.email}")
            raise HTTPException(status_code=400, detail="Invalid profile picture data")
        try:
            file_bytes = base64.b64decode(b64data)
            if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
                logger.error(f"Profile picture too large for user {current_user.email}")
                raise HTTPException(status_code=400, detail="Profile picture exceeds size limit")
            profile_pic_url = await upload_photo_to_cloudinary(file_bytes, current_user.id, "profile")
            updates["profile_pic_url"] = profile_pic_url
            logger.info(f"Profile pic uploaded for {current_user.email}")
        except Exception as e:
            logger.error(f"Profile pic upload failed for {current_user.email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload profile picture")

    # Update standard user fields
    for field in ALLOWED_PROFILE_UPDATE_FIELDS:
        if field in updates and updates[field] is not None:
            setattr(current_user, field, updates[field])

    # Handle hobby updates (exactly 3 hobbies required)
    if "hobby_ids" in updates:
        hobby_ids = updates.pop("hobby_ids")
        if not isinstance(hobby_ids, list) or len(hobby_ids) != 3:
            logger.error(f"Invalid hobby_ids length for user {current_user.email}: {hobby_ids}")
            raise HTTPException(status_code=400, detail="You must select exactly 3 hobbies")

        # Validate hobbies exist in hobbies table
        hobby_query = await db.execute(select(Hobby.id).where(Hobby.id.in_(hobby_ids)))
        valid_hobby_ids = set(str(h) for h in hobby_query.scalars().all())
        if set(map(str, hobby_ids)) != valid_hobby_ids:
            logger.error(f"Invalid hobby IDs provided by user {current_user.email}: {hobby_ids}")
            raise HTTPException(status_code=400, detail="One or more hobby IDs are invalid")

        # Delete existing user hobbies
        await db.execute(delete(UserHobby).where(UserHobby.user_id == current_user.id))

        # Add new user hobbies with rank 1-3
        new_user_hobbies = [
            UserHobby(user_id=current_user.id, hobby_id=hobby_id, rank=rank)
            for rank, hobby_id in enumerate(hobby_ids, start=1)
        ]
        db.add_all(new_user_hobbies)
        logger.info(f"Updated hobbies for user {current_user.email}")

    # Commit all changes
    try:
        await db.commit()
        logger.info(f"User {current_user.email} updated profile successfully")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update profile for user {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Reload user with location and hobbies for response
    try:
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.location),
                selectinload(User.user_hobbies).selectinload(UserHobby.hobby)
            )
            .filter(User.id == current_user.id)
        )
        refreshed_user = result.scalar_one()
    except Exception as e:
        logger.error(f"Failed to reload user after update for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload user data")

    return refreshed_user


# TODO: Implement additional User-related endpoints:
# - POST /users/            : Create new user (if self-registration allowed)
# - GET /users/{id}         : Get user by ID (with detailed relations)
# - PATCH /users/{id}       : Admin update user profile and role
# - DELETE /users/{id}      : Admin delete user
# - GET /users/{id}/matches : Get matches for a user
# - GET /users/{id}/hobbies : Get user's hobbies
# - POST /users/{id}/photos : Upload and manage user photo gallery
# - GET /users/search       : Advanced search with filters and sorting
# - POST /users/{id}/verify : Admin action to verify user manually
# - Additional endpoints for notifications, messaging, events RSVP, etc.