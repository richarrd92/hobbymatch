from fastapi import HTTPException
import hashlib
import asyncio
from logger import logger
import os
from dotenv import load_dotenv
import cloudinary

# Load environment variables
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

# TODO: Change size if needed
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024 # 5MB

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


# Upload base64 image to Cloudinary, return URL
async def upload_base64_image_to_cloudinary(base64_str: str) -> str:

    # Cloudinary expects a data URI scheme with MIME type prefix
    data_uri = f"data:image/jpeg;base64,{base64_str}"
    try:
        resp = cloudinary.uploader.upload(data_uri)
        url = resp.get("secure_url") # Get the secure URL of the uploaded image
        if not url:
            logger.error("No URL returned from Cloudinary")
            raise Exception("No URL returned from Cloudinary")
        return url
    
    # Handle Cloudinary upload errors
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")