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
from utils.cloudinary import upload_photo_to_cloudinary, delete_user_cloudinary_folder
from utils.current_user import get_current_user
import cloudinary.uploader
from firebase_admin import auth as firebase_auth

# Define API router for user-related endpoints
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

@router.get("", response_model=List[UserRead])
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
    """
    Fetch a paginated list of users from the database with optional filtering, searching, and sorting.

    Parameters:
    - skip (int): Number of records to skip for pagination.
    - limit (int): Maximum number of users to return (max 100).
    - search (str, optional): Global search term to match against user name or email.
    - name (str, optional): Filter users whose names partially match this string.
    - email (str, optional): Filter users whose emails partially match this string.
    - role (str, optional): Filter users by their role (e.g., 'admin', 'user').
    - is_verified (bool, optional): Filter by verification status.
    - is_private (bool, optional): Filter by privacy setting.
    - min_age (int, optional): Filter users with age greater than or equal to this.
    - max_age (int, optional): Filter users with age less than or equal to this.
    - sort_by (str): Field to sort by. Must be in ALLOWED_SORT_FIELDS.
    - sort_order (str): 'asc' or 'desc' for ascending or descending order.
    - db (AsyncSession): Database session dependency.
    - current_user (User): The currently authenticated user.

    Returns:
    - List[UserRead]: A list of user objects matching the criteria.

    Raises:
    - HTTPException 400 if invalid sort field is provided.
    - HTTPException 500 on internal server errors.
    """

    # Ensure the current user is an admin before proceeding
    require_admin(current_user)

    try:
        # Build base query with eager loading for related fields
        query = select(User).options(
            selectinload(User.location),
            selectinload(User.photos),
            # TODO: Additional relationships to be loaded here
            # Add selectinload(User.hobbies), 
            # selectinload(User.matches_initiated)
        )

        # Apply global search filter if provided
        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    User.name.ilike(term),
                    User.email.ilike(term)
                    # TODO: Add more field
                )
            )

        # Apply optional individual filters
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

        # Validate and apply sorting
        if sort_by not in ALLOWED_SORT_FIELDS:
            raise HTTPException(status_code=400, detail=f"Invalid sort_by: {sort_by}")
        sort_column = getattr(User, sort_by)
        query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute the query asynchronously
        result = await db.execute(query)
        users = result.scalars().all()
        return users

    except HTTPException:
        raise # Re-raise known HTTP errors
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me", response_model=UserRead)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve the profile information of the currently authenticated user.

    Parameters:
    - db (AsyncSession): Database session dependency.
    - current_user (User): The currently authenticated user.

    Returns:
    - UserRead: User object with profile details including location.

    Raises:
    - HTTPException 404 if the user is not found.
    - HTTPException 500 on internal server errors.
    """

    try:
        # Query the user along with their location relationship
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
        
        return user # Return the user
    
    except HTTPException:
        raise # Re-raise known HTTP errors
    except Exception as e:
        logger.error(f"Failed to load user profile for {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Failed to load profile")

@router.delete("/me")
async def delete_my_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete the currently authenticated user's account from the system.

    This includes:
    - Deleting the user's folder and images from Cloudinary.
    - Removing the user from Firebase Authentication.
    - Deleting the user record from the database.

    Parameters:
    - db (AsyncSession): Database session dependency.
    - current_user (User): The currently authenticated user.

    Returns:
    - dict: Confirmation message on successful deletion.

    Raises:
    - HTTPException 500 on failure to delete account.
    """

    try:
        # Delete user folder and images from Cloudinaryr
        await delete_user_cloudinary_folder(current_user.id.hex)

        # Delete user from Firebase Auth (handle errors gracefully)
        try:
            firebase_auth.delete_user(current_user.firebase_uid)
        except Exception as firebase_error:
            logger.error(f"Firebase deletion failed: {firebase_error}")

        # Delete user from database and commit
        await db.delete(current_user)
        await db.commit()
        return {"message": "Account deleted successfully"}

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete account: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    update: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the currently authenticated user's profile information.

    Supports:
    - Partial updates of allowed user fields (name, age, bio, profile picture URL, location, privacy).
    - Uploading and replacing profile picture from a base64 encoded string.
    - Updating exactly three user hobbies, validating existence.

    Parameters:
    - update (UserProfileUpdate): Pydantic model containing fields to update.
    - db (AsyncSession): Database session dependency.
    - current_user (User): The currently authenticated user.

    Returns:
    - UserRead: Updated user object including location and hobbies.

    Raises:
    - HTTPException 400 if invalid location_id or hobby_ids are provided, or profile picture data is invalid or too large.
    - HTTPException 500 on internal server errors or failed profile picture upload.
    """

    updates = update.dict(exclude_unset=True) # Convert to dict and remove unset fields

    # Validate location if location_id is provided
    if "location_id" in updates:
        loc_result = await db.execute(select(Location).filter(Location.id == updates["location_id"]))
        if not loc_result.scalars().first():
            logger.error(f"Invalid location_id: {updates['location_id']}")
            raise HTTPException(status_code=400, detail="Invalid location_id")

    # Handle profile picture upload if provided as base64 string
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
            
            # Delete old profile picture from Cloudinary if exists
            if current_user.profile_pic_public_id:
                try:
                    cloudinary.uploader.destroy(current_user.profile_pic_public_id)
                except Exception as e:
                    logger.warning(f"Failed to delete old profile pic: {e}")

            # Upload new profile picture to Cloudinary
            upload_result = await upload_photo_to_cloudinary(file_bytes, current_user.id, usage="profile")
            updates["profile_pic_url"] = upload_result["url"]
            updates["profile_pic_public_id"] = upload_result["public_id"]
        except Exception as e:
            logger.error(f"Profile pic upload failed for {current_user.email}: {e}")
            raise HTTPException(status_code=500, detail="Failed to upload profile picture")

    # Update allowed user fields with the new values
    for field in ALLOWED_PROFILE_UPDATE_FIELDS:
        if field in updates and updates[field] is not None:
            setattr(current_user, field, updates[field])

    # Handle hobby updates: exactly 3 hobbies required
    if "hobby_ids" in updates:
        hobby_ids = updates.pop("hobby_ids")
        if not isinstance(hobby_ids, list) or len(hobby_ids) != 3:
            logger.error(f"Invalid hobby_ids length for user {current_user.email}: {hobby_ids}")
            raise HTTPException(status_code=400, detail="You must select exactly 3 hobbies")

        # Validate hobbies exist in the Hobby table
        hobby_query = await db.execute(select(Hobby.id).where(Hobby.id.in_(hobby_ids)))
        valid_hobby_ids = set(str(h) for h in hobby_query.scalars().all())
        if set(map(str, hobby_ids)) != valid_hobby_ids:
            logger.error(f"Invalid hobby IDs provided by user {current_user.email}: {hobby_ids}")
            raise HTTPException(status_code=400, detail="One or more hobby IDs are invalid")

        # Remove existing user hobbies
        await db.execute(delete(UserHobby).where(UserHobby.user_id == current_user.id))

        # Add new hobbies with ranks 1 to 3
        new_user_hobbies = [
            UserHobby(user_id=current_user.id, hobby_id=hobby_id, rank=rank)
            for rank, hobby_id in enumerate(hobby_ids, start=1)
        ]
        db.add_all(new_user_hobbies)

    # Commit all changes to the database
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update profile for user {current_user.email}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Reload updated user with related location and hobbies for response
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