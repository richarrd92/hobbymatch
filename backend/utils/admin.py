from fastapi import HTTPException
from models import User, UserRole
from logger import logger

def require_admin(current_user: User):
    """
    Verify that the current user has admin privileges.

    Parameters:
    - current_user (User): The user object representing the currently authenticated user.

    Returns:
    - User: Returns the current_user if they have admin privileges.

    Raises:
    - HTTPException 403 Forbidden: If the user does not have admin privileges.

    Note:
    - Currently checks if role is not `UserRole.user`, but TODO indicates to change this to `UserRole.admin` later.
    """
    
    if current_user.role != UserRole.user: # TODO: Change to admin later
        logger.warning(f"Unauthorized access attempt by {current_user.email}")
        raise HTTPException(status_code=403, detail="Not authorized - admin required")
    return current_user