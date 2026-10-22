from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"

    class Config:
        env_file = ".env"

settings = Settings()