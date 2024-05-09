from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:111111@localhost:5432/abc"
    API_KEY_JWT: str = "your_jwt_api_key"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "example@example.com"
    MAIL_PASSWORD: str = "your_email_password"
    MAIL_FROM: str = "example@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.example.com"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CLD_NAME: str = "cloudinary_name"
    CLD_API_KEY: str = "your_cloudinary_api_key"
    CLD_API_SECRET: str = "your_cloudinary_api_secret"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8"
    )  # noqa


config = Settings()
