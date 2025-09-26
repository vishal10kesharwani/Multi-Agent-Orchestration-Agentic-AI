"""
Database connection and session management
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData
import redis
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Database engine and session
engine = None
async_session_maker = None
redis_client = None

# Base class for SQLAlchemy models
Base = declarative_base()
metadata = MetaData()


async def init_database():
    """Initialize database connections"""
    global engine, async_session_maker, redis_client
    
    try:
        # Convert database URL to async format if needed
        database_url = settings.DATABASE_URL
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("sqlite://"):
            database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        else:
            database_url = "sqlite+aiosqlite:///./multiagent.db"
        
        engine = create_async_engine(
            database_url,
            echo=settings.LOG_LEVEL == "DEBUG",
            future=True,
            pool_pre_ping=True
        )
        
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize Redis connection with error handling
        try:
            redis_client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=5)
            # Test connection
            redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Continuing without Redis.")
            redis_client = None
        
        # Create tables
        from backend.database.models import Agent, Task, Message, ExecutionLog, ResourceUsage
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        return engine, async_session_maker
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def get_db_session() -> AsyncSession:
    """Get database session"""
    if async_session_maker is None:
        await init_database()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis_client():
    """Get Redis client instance"""
    global redis_client
    if redis_client is None:
        try:
            redis_client = redis.Redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5
            )
            redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Continuing without Redis.")
            redis_client = None
    return redis_client


async def close_database():
    """Close database connections"""
    global engine, redis_client
    
    if engine:
        await engine.dispose()
        logger.info("Database engine disposed")
    
    if redis_client:
        try:
            redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")


def get_sync_session():
    """Get synchronous session for non-async contexts"""
    if async_session_maker is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    # For sync contexts, we need to handle this differently
    import asyncio
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, this shouldn't be called
            raise RuntimeError("Use get_db_session() in async contexts")
    except RuntimeError:
        # No event loop, we can create one
        pass
    
    # This is a fallback for sync contexts
    return async_session_maker()
