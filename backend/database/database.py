import logging
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

from ..models import Base

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")

IS_DEVELOPMENT = os.getenv("APP_ENV").lower() == "development"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

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


# async def initialize_db():
#     """
#     Initialize the database with tables and default data
#     """
#     # Create tables
#     await create_tables()
    
#     # Add default data
#     async with async_session() as session:
#         # Check if admin user exists
#         admin_user = await session.get(User, 1)
#         if not admin_user:
#             admin_user = User(
#                 username="admin",
#                 email="admin@example.com",
#                 password_hash="hashed_password"  # In production, use proper password hashing
#             )
#             session.add(admin_user)
#             await session.commit()