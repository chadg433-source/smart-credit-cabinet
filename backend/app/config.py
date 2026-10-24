from pydantic_settings import BaseSettings
from uuid import UUID


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"
    jwt_secret_key: str
    demo_user_id: UUID = UUID("ba5be38a-2d60-4566-af13-717ebc165f74")


    class Config:
        env_file = ".env"

settings = Settings()