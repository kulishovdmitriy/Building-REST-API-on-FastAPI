from pydantic import BaseModel, Field, EmailStr
from src.database.models import Role


class UserSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=25)
    email: str = EmailStr
    password: str = Field(..., min_length=6, max_length=10)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Role | None

    class Config:
        from_attributes = True
