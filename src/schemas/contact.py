from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime
from src.schemas.user import UserResponseSchema


class ContactCreateSchema(BaseModel):
    first_name: str = Field(..., min_length=3, max_length=25)
    last_name: str = Field(..., min_length=3, max_length=25)
    email: str = Field(..., min_length=3, max_length=75)
    phone_number: str = Field(..., min_length=3, max_length=15)
    birthday: date = Field(...)

    @field_validator("birthday")
    def check_date_format(cls, v):
        if not isinstance(v, date):
            raise ValueError("Invalid date format")
        return v


class ContactUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, min_length=3, max_length=25)
    last_name: Optional[str] = Field(None, min_length=3, max_length=25)
    email: Optional[str] = Field(None, min_length=3, max_length=75)
    phone_number: Optional[str] = Field(None, min_length=3, max_length=15)
    birthday: Optional[date] = Field(None)


class ContactResponseSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponseSchema | None

    class Config:
        from_attributes = True
