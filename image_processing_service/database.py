from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from image_processing_service.settings import settings

engine = create_async_engine(settings.DATABASE_URL)


async def get_session():
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
