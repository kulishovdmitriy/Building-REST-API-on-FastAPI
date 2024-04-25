from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from src.schemas.user import UserResponseSchema
from src.servises.auth import auth_service
from src.database.models import User
from fastapi.responses import FileResponse

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/me', response_model=UserResponseSchema, dependencies=[Depends(RateLimiter(times=4, seconds=30))])
async def get_user(user: User = Depends(auth_service.get_current_user)):
    return user
