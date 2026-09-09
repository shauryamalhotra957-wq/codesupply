from datetime import datetime

from app.core.config import get_settings


class VulnerabilityCache:
    """Transparent local cache for OSV responses."""

    async def get(self, ecosystem: str, name: str, version: str, db_session) -> dict | None:
        """Get cached response if fresh (within TTL)."""
        # In a real app, you would query the DB for this entry.
        # For MVP we can just assume no cache or integrate DB.
        # Stubbed for schema alignment.
        return None

    async def set(self, ecosystem: str, name: str, version: str, response: dict, db_session):
        """Cache a response."""
        # Insert into DB cache table

    async def is_fresh(self, cached_at: datetime) -> bool:
        """Check if cache entry is within TTL."""
        settings = get_settings()
        from datetime import timedelta, timezone

        now = datetime.now(timezone.utc)
        return now - cached_at < timedelta(hours=settings.OSV_CACHE_TTL_HOURS)
