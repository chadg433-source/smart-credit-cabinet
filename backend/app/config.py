from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://alfa:alfa@localhost:5432/credit"

    # LLM (Ollama, модели с открытыми весами)
    llm_base_url: str = "http://localhost:11434"
    llm_model: str = "qwen3:4b"
    llm_timeout_seconds: float = 30.0

    class Config:
        env_file = ".env"

settings = Settings()