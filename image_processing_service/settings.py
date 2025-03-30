from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str = 'sqlite+aiosqlite:///database.db'
    # sync database url for alembic
    MIGRATIONS_DATABASE_URL: str = 'sqlite:///database.db'
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / 'uploads'

    CELERY_BROKER_URL: str = 'pyamqp://guest:guest@localhost//'


settings = Settings()
