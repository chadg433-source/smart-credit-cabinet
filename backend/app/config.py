from pydantic_settings import BaseSettings
from uuid import UUID


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"
    jwt_secret_key: str
    demo_user_id: UUID = UUID("ba5be38a-2d60-4566-af13-717ebc165f74")
    demo_business_id: UUID = UUID("a1b8de91-8d55-49b8-9e7b-8bda0983d697")
    demo_product_id: UUID = UUID("6f41de33-1393-41e3-bef3-d623a743e711")


    class Config:
        env_file = ".env"

settings = Settings()