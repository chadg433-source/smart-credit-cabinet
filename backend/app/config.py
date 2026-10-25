from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"

    # LLM: любой сервер с OpenAI-совместимым API (по умолчанию llama.cpp в контейнере `llm`)
    llm_url: str = "http://localhost:8080"
    llm_model: str = "t-lite-it-2.1"
    llm_timeout_seconds: float = 90.0  # 8B-модель на CPU отвечает десятки секунд

    class Config:
        env_file = ".env"

settings = Settings()