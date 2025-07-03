from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
import base64
import hashlib
import asyncio
import time

from models import User, Location, UserRole
from schemas import UserRead, UserProfileUpdate
from database import get_db
from .auth import get_current_user
from logger import logger

import cloudinary.uploader

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

# Helper: Ensure the user is an Admin
def require_admin(current_user: User):
    if current_user.role != UserRole.user: # TODO: Change to admin later
        logger.warning(f"Unauthorized access attempt by {current_user.email}")
        raise HTTPException(status_code=403, detail="Not authorized - admin required")
    return current_user

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

# Upload a photo to Cloudinary and return the URL
async def upload_photo_to_cloudinary(file_bytes: bytes, user_id: int, tag: str = None) -> str:
    # Check image size limit
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        max_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
        logger.error(f"Image too large for {user_id}: {max_mb:.1f} MB")
        raise HTTPException(status_code=400, detail=f"Image too large (max {max_mb:.1f} MB)")

    # Generate unique public ID for Cloudinary
    public_id = f"user_{user_id}_{tag or hashlib.md5(file_bytes).hexdigest()}"
    max_retries = 3  # Number of retries

    # Try uploading with retries
    for attempt in range(max_retries):
        try:
            # Upload to Cloudinary
            resp = cloudinary.uploader.upload(
                file_bytes,
                resource_type="image",
                folder="user_photos",
                public_id=public_id,
                overwrite=True,
                invalidate=True,
            )
            url = resp.get("secure_url")

            # Check if upload was successful
            if not url:
                logger.error("Cloudinary upload did not return a URL")
                raise Exception("Cloudinary upload did not return a URL")
            return url
        
        # Handle Cloudinary upload errors
        except Exception as e:
            logger.error(f"Cloudinary upload attempt {attempt + 1} failed: {e}")

            # Retry after delay if attempts remain
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                # Raise error after max retries
                logger.error(f"Cloudinary upload failed after {max_retries} attempts")
                raise HTTPException(status_code=500, detail="Failed to upload image")

# Update the current user's profile with optional fields and profile picture upload
@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Extract only provided fields
    updates = update.dict(exclude_unset=True)

    # Validate location_id if provided
    if "location_id" in updates:
        loc_result = await db.execute(select(Location).filter(Location.id == updates["location_id"]))

        # Check if location exists
        if not loc_result.scalars().first():
            logger.error(f"Invalid location_id: {updates['location_id']}")
            raise HTTPException(status_code=400, detail="Invalid location_id")

    # Handle profile picture upload (single image only)
    if "profile_pic_base64" in updates:
        b64data = updates.pop("profile_pic_base64")

        # Validate base64 data
        if not b64data or len(b64data) < 100:
            logger.error(f"Invalid profile picture data: {b64data}")
            raise HTTPException(status_code=400, detail="Invalid profile picture data")
        try:
            # Decode base64 data
            file_bytes = base64.b64decode(b64data)
            profile_pic_url = await upload_photo_to_cloudinary(file_bytes, current_user.id, "profile") # Upload
            updates["profile_pic_url"] = profile_pic_url
            logger.info(f"Profile pic uploaded for {current_user.email}")
        
        # Handle Cloudinary upload errors
        except Exception as e:
            logger.error(f"Profile pic upload failed for {current_user.email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload profile picture")
        
    # TODO: Implement upload and storage for 3 additional profile photos (e.g., photos_base64[])
    # - Accept multiple base64 strings
    # - Decode and upload each to Cloudinary with distinct tags (e.g., "photo1", "photo2", etc.)
    # - Store URLs in a separate related model or field

    # Update allowed user fields
    for field in ALLOWED_PROFILE_UPDATE_FIELDS:
        if field in updates and updates[field] is not None:
            setattr(current_user, field, updates[field])

    # Commit updates or rollback on error
    try:
        await db.commit()
        logger.info(f"User {current_user.email} updated profile")
    except Exception as e:
        await db.rollback()
        logger.error(f"Profile update failed for user {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Reload user with location to avoid lazy loading issues
    # TODO: Add selectinload for hobbies, matches_initiated, matches_received as project expands
    try:
        result = await db.execute(
            select(User)
            .options(selectinload(User.location))
            .filter(User.id == current_user.id)
        )

        # Updated user with location preloaded
        refreshed_user = result.scalar_one()

    except Exception as e:
        logger.error(f"Failed to reload user after update: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload user data")

    logger.info(f"User {refreshed_user.email} updated profile")
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