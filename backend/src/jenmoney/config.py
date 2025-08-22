from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "JenMoney Backend"
    version: str = "0.1.0"
    api_v1_str: str = "/api/v1"

    database_url: str = "sqlite:///./data/finance.db"

    cors_origins: list[str] = [
        "http://localhost:3000",  # Create React App default
        "http://localhost:5173",  # Vite default (our main dev port)
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


settings = Settings()
