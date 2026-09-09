import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.models.models import Base


@pytest_asyncio.fixture
async def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def settings():
    return Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        MAX_UPLOAD_SIZE_MB=10,
        MAX_ARCHIVE_FILES=100,
        MAX_EXTRACTED_SIZE_MB=50,
        TEMP_DIR="./test_tmp",
    )
