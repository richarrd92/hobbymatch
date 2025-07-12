from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from uuid import UUID
from models import Hobby, User, UserHobby
from schemas.hobbies import HobbyCreate, HobbyRead, HobbyUpdate, HobbyUpdateRequest, UserHobbyRead
from database import get_db
from utils.current_user import get_current_user
from utils.admin import require_admin
from models import HobbyCategory
from logger import logger

# Define API router for hobby endpoints
router = APIRouter(prefix="/hobbies", tags=["Hobbies"])

@router.get("/categories", response_model=list[str])
async def get_hobby_categories():
    """
    Fetch all hobby categories as a list of strings.

    Returns:
    - List[str]: Available hobby categories (Enum values).
    """
    return [category.value for category in HobbyCategory]

@router.get("", response_model=list[HobbyRead])
async def get_all_hobbies(db: AsyncSession = Depends(get_db)):
    """
    Fetch all hobbies in the system (available to all users).

    Parameters:
    - db (AsyncSession): Dependency-injected database session.

    Returns:
    - List[HobbyRead]: All hobbies in the database.

    Raises:
    - HTTP 500 on database errors.
    """
    try:
        result = await db.execute(select(Hobby))
        return result.scalars().all()
    except Exception as e:
        logger.error(f"Error fetching hobbies: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching hobbies: {str(e)}")

@router.post("", response_model=HobbyRead, status_code=status.HTTP_201_CREATED)
async def create_hobby(
    hobby_in: HobbyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    """
    Admin-only: Create a new hobby.

    Parameters:
    - hobby_in (HobbyCreate): Hobby name and category.
    - db (AsyncSession): DB session.
    - current_user (User): Current authenticated user (must be admin).

    Returns:
    - HobbyRead: The newly created hobby.
    """
    require_admin(current_user)

    # Create new hobby
    hobby = Hobby(
        name=hobby_in.name.strip(),
        category=hobby_in.category,
        created_by=current_user.id
    )

    # Add to DB
    db.add(hobby)
    await db.commit()
    await db.refresh(hobby)
    return hobby

@router.put("/me", status_code=status.HTTP_200_OK)
async def update_user_hobby_ids(
    payload: HobbyUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):  
    """
    Replace a user's hobby preferences (up to 3 hobbies).

    Parameters:
    - payload (HobbyUpdateRequest): List of hobby UUIDs.
    - db (AsyncSession): DB session.
    - current_user (User): Authenticated user.

    Returns:
    - dict: Confirmation message.

    Raises:
    - HTTP 400 if more than 3 hobbies or invalid hobby IDs are provided.
    """
    if len(payload.hobby_ids) > 3:
        raise HTTPException(status_code=400, detail="You can select up to 3 hobbies only")

    # Make sure all hobbies exist
    result = await db.execute(select(Hobby.id).where(Hobby.id.in_(payload.hobby_ids)))
    found_ids = set(r[0] for r in result.all())
    if set(payload.hobby_ids) != found_ids:
        logger.error("One or more hobby IDs are invalid")
        raise HTTPException(status_code=400, detail="One or more hobby IDs are invalid")

    # Clear and replace existing user hobbies
    await db.execute(delete(UserHobby).where(UserHobby.user_id == current_user.id))

    # Add new ones
    new_user_hobbies = [
        UserHobby(user_id=current_user.id, hobby_id=hobby_id, rank=index)
        for index, hobby_id in enumerate(payload.hobby_ids, start=1)
    ]

    # Add to DB
    db.add_all(new_user_hobbies)
    await db.commit()

    return {"detail": "Hobbies updated"}

@router.put("/{hobby_id}", response_model=HobbyRead)
async def update_hobby(
    hobby_id: UUID,
    hobby_in: HobbyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin-only: Update an existing hobby's name or category.

    Parameters:
    - hobby_id (UUID): ID of the hobby to update.
    - hobby_in (HobbyUpdate): New values.
    - db (AsyncSession): DB session.
    - current_user (User): Must be admin.

    Returns:
    - HobbyRead: Updated hobby object.

    Raises:
    - HTTP 404 if hobby not found.
    """

    require_admin(current_user) # must be an admin

    # Check if the hobby exists
    result = await db.execute(select(Hobby).where(Hobby.id == hobby_id))
    hobby = result.scalar_one_or_none()
    if not hobby:
        logger.error(f"Hobby not found for ID: {hobby_id}")
        raise HTTPException(status_code=404, detail="Hobby not found")

    # Update
    if hobby_in.name:
        hobby.name = hobby_in.name.strip()
    if hobby_in.category:
        hobby.category = hobby_in.category

    # Add to DB
    await db.commit()
    await db.refresh(hobby)
    return hobby

@router.delete("/{hobby_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hobby(
    hobby_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Admin-only: Delete a hobby by ID.

    Parameters:
    - hobby_id (UUID): Hobby to delete.
    - db (AsyncSession): DB session.
    - current_user (User): Must be admin.

    Returns:
    - 204 No Content on success.

    Raises:
    - HTTP 404 if hobby not found.
    """

    require_admin(current_user)

    # Check if the hobby exists
    result = await db.execute(select(Hobby).where(Hobby.id == hobby_id))
    hobby = result.scalar_one_or_none()
    if not hobby:
        logger.error(f"Hobby not found for ID: {hobby_id}")
        raise HTTPException(status_code=404, detail="Hobby not found")

    # Delete from db
    await db.delete(hobby)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/users/me/hobbies", response_model=list[UserHobbyRead])
async def get_my_hobbies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve hobbies associated with the current user.

    Parameters:
    - db (AsyncSession): DB session.
    - current_user (User): Authenticated user.

    Returns:
    - List[UserHobbyRead]: User's selected hobbies with rank.
    """

    # Get current user's hobbies
    result = await db.execute(
        select(UserHobby).where(UserHobby.user_id == current_user.id).options(selectinload(UserHobby.hobby))
    )
    return result.scalars().all()

@router.put("/users/me/hobbies", response_model=list[UserHobbyRead])
async def replace_my_hobbies(
    hobbies_in: list[HobbyCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Replace current user's hobbies with a new list (up to 3).
    If a hobby does not exist, it is created automatically.

    Parameters:
    - hobbies_in (List[HobbyCreate]): New hobby list (max 3).
    - db (AsyncSession): DB session.
    - current_user (User): Authenticated user.

    Returns:
    - List[UserHobbyRead]: Updated user hobbies.

    Raises:
    - HTTP 400 for too many hobbies or invalid category.
    - HTTP 409 if duplicates occur.
    """

    # Validate hobbies
    if len(hobbies_in) > 3:
        raise HTTPException(status_code=400, detail="You can select up to 3 hobbies only")

    # Validate hobby categories
    for h in hobbies_in:
        if h.category not in HobbyCategory._value2member_map_:
            logger.error(f"Invalid hobby category: {h.category}")
            raise HTTPException(status_code=400, detail=f"Invalid hobby category: {h.category}")

    new_user_hobbies = []  # List to store new UserHobby objects

    try:
        # Delete existing hobbies
        await db.execute(delete(UserHobby).where(UserHobby.user_id == current_user.id))

        # Create new hobbies
        for index, hobby_in in enumerate(hobbies_in, start=1):
            result = await db.execute(
                select(Hobby).where(
                    Hobby.name.ilike(hobby_in.name.strip()),
                    Hobby.category == hobby_in.category
                )
            )
            hobby = result.scalar_one_or_none()

            # If hobby doesn't exist, create it
            if not hobby:
                hobby = Hobby(
                    name=hobby_in.name.strip(),
                    category=hobby_in.category,
                    created_by=current_user.id
                )
                db.add(hobby)
                await db.flush()

            # Create UserHobby
            user_hobby = UserHobby(
                user_id=current_user.id,
                hobby_id=hobby.id,
                rank=index
            )
            db.add(user_hobby)
            new_user_hobbies.append(user_hobby)

        await db.commit()

        # Refresh hobbies
        for uh in new_user_hobbies:
            await db.refresh(uh)

    except IntegrityError:
        await db.rollback()
        logger.error("Duplicate hobbies detected")
        raise HTTPException(status_code=409, detail="Duplicate hobbies detected")
    except Exception:
        await db.rollback()
        raise
    
    return new_user_hobbies

