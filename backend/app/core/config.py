from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_ROOT.parent


class Settings(BaseSettings):
    app_name: str = "医学刷题平台"
    environment: str = "development"
    secret_key: str = "please-change-this-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite:///./medical_quiz.db"
    backend_cors_origins: str = "http://localhost:5173,http://localhost:3000"
    upload_dir: str = "uploads"
    max_upload_size_mb: int = 10
    default_admin_username: str = "admin"
    default_admin_password: str = "admin123456"

    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env.example", PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]

    @property
    def resolved_database_url(self) -> str:
        return resolve_database_url(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def backend_root() -> Path:
    return BACKEND_ROOT


def resolve_backend_path(path: str) -> Path:
    value = Path(path)
    return value if value.is_absolute() else backend_root() / value


def resolve_database_url(url: str) -> str:
    if not url.startswith("sqlite:///") or url.startswith("sqlite:////"):
        return url
    db_path = url.replace("sqlite:///", "", 1)
    if db_path == ":memory:":
        return url
    value = Path(db_path)
    resolved = value if value.is_absolute() else resolve_backend_path(db_path)
    return f"sqlite:///{resolved}"
