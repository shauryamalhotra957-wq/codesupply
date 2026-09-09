from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./codesupply.db"
    MAX_UPLOAD_SIZE_MB: int = 100
    MAX_ARCHIVE_FILES: int = 10000
    MAX_EXTRACTED_SIZE_MB: int = 500
    OSV_API_URL: str = "https://api.osv.dev"
    OSV_BATCH_SIZE: int = 1000
    OSV_CACHE_TTL_HOURS: int = 24
    SCAN_RETENTION_DAYS: int = 30
    TEMP_DIR: str = "./tmp"
    ALLOWED_REGISTRY_HOSTS: list[str] = [
        "api.osv.dev",
        "registry.npmjs.org",
        "pypi.org",
        "repo.maven.apache.org",
    ]

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
