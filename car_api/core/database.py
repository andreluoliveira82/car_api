# car_api/core/database.py
# ==============================================================================
# File: car_api/core/database.py
# Description: This module sets up the database connection and session management for the Car API using SQLAlchemy.
# ==============================================================================

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from car_api.core.settings import settings


# Create the asynchronous database engine using the connection URL from settings
engine = create_async_engine(settings.DATABASE_URL)

# Function to create a new asynchronous database session
async def get_db_session() -> AsyncSession:
    """
    Asynchronous generator function that provides a database session for use in API endpoints.
    This function creates a new AsyncSession, yields it for use, and ensures that the session is properly closed after use.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
