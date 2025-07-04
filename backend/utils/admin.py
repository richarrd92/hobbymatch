from fastapi import HTTPException
from models import User, UserRole
from logger import logger

# Helper: Ensure the user is an Admin
def require_admin(current_user: User):
    if current_user.role != UserRole.user: # TODO: Change to admin later
        logger.warning(f"Unauthorized access attempt by {current_user.email}")
        raise HTTPException(status_code=403, detail="Not authorized - admin required")
    return current_user