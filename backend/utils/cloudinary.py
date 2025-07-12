from fastapi import HTTPException
import asyncio
from logger import logger
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import uuid
from io import BytesIO 

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

async def upload_photo_to_cloudinary(file_bytes: bytes, user_id: int, usage: str = "post") -> dict:
    """
    Upload an image file (raw bytes) to Cloudinary under a user-specific folder with usage context

    Parameters:
    - file_bytes (bytes): Raw bytes of the image to upload.
    - user_id (int): Unique ID of the user uploading the image; used for folder pathing.
    - usage (str): Purpose of the image, either 'post' or 'profile' (default 'post').

    Returns:
    - dict: Contains 'url' (secure URL of uploaded image) and 'public_id' (Cloudinary identifier).

    Raises:
    - HTTPException 400 if the image size exceeds the limit or usage is invalid.
    - HTTPException 500 if upload fails after retries.
    """

    # Check image size
    if len(file_bytes) > MAX_IMAGE_SIZE_BYTES:
        max_mb = MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
        logger.error(f"Image too large for user {user_id}: {max_mb:.1f} MB")
        raise HTTPException(status_code=400, detail=f"Image too large (max {max_mb:.1f} MB)")

    # Check usage
    if usage not in ["post", "profile"]:
        raise HTTPException(status_code=400, detail="Invalid usage type. Must be 'post' or 'profile'.")

    # Define the folder based on usage
    folder = f"{'post_images' if usage == 'post' else 'user_profiles'}/user_{user_id}"

    # Generate a unique public_id
    unique_suffix = uuid.uuid4().hex[:10]
    public_id = f"{folder}/{usage}_{unique_suffix}"

    # Upload to Cloudinary
    for attempt in range(3):
        try:
            resp = cloudinary.uploader.upload(
                BytesIO(file_bytes),
                resource_type="image",
                folder=folder,
                public_id=public_id,
                overwrite=False,  # don't overwrite
                invalidate=True,
            )
            url = resp.get("secure_url")
            if not url:
                raise Exception("Cloudinary upload did not return a URL")
            return {
                "url": url,
                "public_id": resp.get("public_id")
            }
        except Exception as e:
            logger.error(f"Cloudinary upload attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(1)
            else:
                raise HTTPException(status_code=500, detail="Failed to upload image to Cloudinary")
            
async def upload_base64_image_to_cloudinary(base64_str: str) -> str:
    """
    Upload a base64-encoded image string to Cloudinary and return the accessible URL

    Parameters:
    - base64_str (str): Base64 encoded image data (without data URI prefix).

    Returns:
    - str: Secure URL of the uploaded image.

    Raises:
    - HTTPException 500 if the upload fails or no URL is returned.
    """

    data_uri = f"data:image/jpeg;base64,{base64_str}"

    try:
        resp = cloudinary.uploader.upload(data_uri)
        url = resp.get("secure_url")
        if not url:
            logger.error("No URL returned from Cloudinary")
            raise Exception("No URL returned from Cloudinary")
        return url

    except Exception as e:
        logger.exception("Cloudinary upload error")
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")
    

async def delete_user_cloudinary_folder(user_id: str):
    """
    Delete all Cloudinary resources under the folder associated with the given user,
    then delete the folder itself.

    Parameters:
    - user_id (str): The user ID string, used to identify the Cloudinary folder to delete.

    Returns:
    - None

    Raises:
    - HTTPException 500 if deletion of resources or folder fails.
    """

    try:
        folder_path = f"user_photos/{user_id}"
        cloudinary.api.delete_resources_by_prefix(folder_path)
        cloudinary.api.delete_folder(folder_path)
    except Exception as e:
        logger.error(f"Failed to delete Cloudinary folder for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to clean up user media")