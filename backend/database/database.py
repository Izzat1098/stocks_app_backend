import logging
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..models import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set!")

IS_DEVELOPMENT = os.getenv("APP_ENV", "development").lower() == "development"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def test_db_connection():
    """Test database connection on startup"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logging.info("[SUCCESS] Database connection successful")
        return True

    except Exception as e:
        logging.error(f"[FAIL] Database connection failed: {e}")
        raise RuntimeError(f"Cannot connect to database: {e}")


async def get_db():
    """
    Dependency to get database session
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    Create all database tables
    """
    try:
        await test_db_connection()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logging.info("[SUCCESS] Database tables created")

    except Exception as e:
        logging.error(f"[FAIL] Failed to create database tables: {e}")
        raise
