import asyncio
from sqlmodel import SQLModel
from app.db import async_engine
from app.config import get_settings

settings = get_settings()

async def async_reset_db():
    if settings.environment != "development":
        raise RuntimeError("Cannot reset db outside development environment")
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all, cascade=True)

if __name__ == "__main__":
    asyncio.run(async_reset_db())