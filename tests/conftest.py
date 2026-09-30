import pytest
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from api_gateway.repository.models import Base
from api_gateway.config.settings import settings


engine = create_async_engine(
    settings.test_database_url,
    echo = False,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture
async def setup_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def db(setup_database):
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()