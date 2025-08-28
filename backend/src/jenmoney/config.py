from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JenMoney Backend"
    version: str = "0.1.0"
    api_v1_str: str = "/api/v1"

    database_url: str = "sqlite:///./data/finance.db"
    
    # Production environment variables
    environment: str = "development"  # development, production
    secret_key: str = "dev-secret-key-change-in-production"
    
    # PostgreSQL settings (used when DATABASE_URL is postgres://)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "jenmoney"
    postgres_password: str = "password"
    postgres_db: str = "jenmoney"

    cors_origins: list[str] = [
        "http://localhost:3000",  # Create React App default
        "http://localhost:5173",  # Vite default (our main dev port)
        "http://127.0.0.1:5173",  # Alternative localhost address
    ]

    debug: bool = True

    model_config = SettingsConfigDict(
        env_prefix="JENMONEY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def database_path(self) -> Path:
        if self.database_url.startswith("sqlite:///"):
            path = Path(self.database_url.replace("sqlite:///", ""))
            return path.resolve()
        return Path("data/finance.db")
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
