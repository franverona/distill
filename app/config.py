from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(env_file=".env")

    environment: str = "development"  # set to "production" in prod

    database_url: str = "sqlite:///./distill.db"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    max_content_chars: int = 50_000

    # Comma-separated lists, e.g. "example.com,bad.org"
    url_blocklist: str = ""
    url_allowlist: str = ""  # if non-empty, ONLY these domains are permitted

    rate_limit_per_minute: int = 10

    @property
    def blocked_domains(self) -> list[str]:
        return [d.strip() for d in self.url_blocklist.split(",") if d.strip()]

    @property
    def allowed_domains(self) -> list[str]:
        return [d.strip() for d in self.url_allowlist.split(",") if d.strip()]


settings = Settings()
