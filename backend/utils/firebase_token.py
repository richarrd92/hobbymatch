from fastapi import HTTPException
from firebase_admin import auth
from logger import logger

# Verifies Firebase ID token and returns decoded payload
def verify_firebase_token(id_token: str):
    try:
        decoded = auth.verify_id_token(id_token)

        # Check if email is verified
        if not decoded.get("email_verified", False):
            logger.error("Email not verified")
            raise HTTPException(status_code=401, detail="Email not verified")
        logger.info("Token verified")
        return decoded # Decoded token
    
    # Handle token verification errors
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
