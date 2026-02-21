from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # TODO: Add fields for each variable defined in .env.example
    # Hint: pydantic-settings maps env var names to field names automatically
    # Example:
    #   database_url: str = "sqlite:///./distill.db"

    class Config:
        env_file = ".env"


# TODO: Instantiate Settings so the rest of the app can import it
# Example:
#   settings = Settings()
