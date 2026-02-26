from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    environment: str = "development"  # set to "production" in prod

    database_url: str = "sqlite:///./distill.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"


settings = Settings()
