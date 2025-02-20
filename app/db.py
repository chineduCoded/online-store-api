from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel, create_engine
from app.logging_config.logger import logger
from fastapi import HTTPException, status

from app.config import get_settings

settings = get_settings()

async_engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

async def get_session():
    try:
        async with AsyncSession(async_engine) as session:
            yield session
    except SQLAlchemyError as e:
        logger.exception(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed."
        )
    finally:
        await session.close()
    
sync_engine = create_engine(
    settings.sync_database_url,
    echo=False
)

async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)