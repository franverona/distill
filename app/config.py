from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    database_url: str = "sqlite:///./distill.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    class Config:
        env_file = ".env"


settings = Settings()
