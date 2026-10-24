from pydantic_settings import BaseSettings
from uuid import UUID


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"
    jwt_secret_key: str
    demo_user_id: UUID = UUID("12345678-1234-5678-1234-567812345678")


    class Config:
        env_file = ".env"

settings = Settings()