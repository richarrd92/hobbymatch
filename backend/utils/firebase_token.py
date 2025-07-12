from fastapi import HTTPException
from firebase_admin import auth
from logger import logger

def verify_firebase_token(id_token: str):
    """
    Verify a Firebase ID token and return the decoded token payload.

    Parameters:
    - id_token (str): The Firebase ID token string to verify.

    Returns:
    - dict: The decoded token payload containing user information.

    Raises:
    - HTTPException 401 Unauthorized: If the token is invalid or verification fails.
    - HTTPException 401 Unauthorized: If the user's email is not verified.

    Behavior:
    - Uses Firebase Admin SDK's `verify_id_token` method to verify token authenticity.
    - Logs errors for invalid tokens or unverified emails.
    """
    
    try:
        decoded = auth.verify_id_token(id_token)

        # Ensure the user's email has been verified
        if not decoded.get("email_verified", False):
            logger.error("Email not verified")
            raise HTTPException(status_code=401, detail="Email not verified")
        return decoded # Return the decoded token payload
    
    # Handle token verification errors
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
