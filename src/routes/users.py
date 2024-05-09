import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import config
from src.database.db import get_db
from src.schemas.user import UserResponseSchema
from src.servises.auth import auth_service
from src.database.models import User
from src.repository import users as repositories_user

router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponseSchema,
    dependencies=[Depends(RateLimiter(times=4, seconds=30))],
)
async def get_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_user function is a dependency that will be injected into the
    get_current_user function. It will return the user object if it exists,
    otherwise it will raise an HTTPException with a 401 status code.

    :param user: User: Define the type of the parameter
    :return: The user object

    """
    return user


@router.patch(
    "/avatar",
    response_model=UserResponseSchema,
    dependencies=[Depends(RateLimiter(times=4, seconds=30))],
)
async def get_avatar(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    The get_avatar function is used to upload a new avatar for the user.

    :param file: UploadFile: Receive the file from the client
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Pass the database session to the repository layer
    :param : Get the current user from the database
    :return: The user object with the updated avatar_url field

    """
    public_id = f"Web16/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=100, height=150, crop="fill", version=res.get("version")
    )
    user = await repositories_user.update_avatar_url(user.email, res_url, db)
    return user
