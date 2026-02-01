"""SQLAlchemy database configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.infrastructure.db.models import Base


def get_database_url() -> str:
    """Build async database URL from settings.

    Converts Supabase URL to asyncpg connection string.
    """
    url = settings.DATABASE_URL
    # Convert postgres:// to postgresql+asyncpg://
    return url.replace("postgres://", "postgresql+asyncpg://").replace(
        "postgresql://", "postgresql+asyncpg://"
    )


# Engine singleton
_engine = None
_session_factory = None


def get_engine():
    """Get or create the async engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create the async session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncSession:
    """Get an async database session."""
    factory = get_session_factory()
    async with factory() as session:
        yield session


# Re-export Base for Alembic
__all__ = ["Base", "get_engine", "get_session", "get_database_url"]
