import uuid
from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from image_processing_service.database import get_session
from image_processing_service.main import app
from image_processing_service.models import Image, table_registry
from image_processing_service.utils.hashing import get_password_hash
from tests.factories import UserFactory


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password

    return user


@pytest_asyncio.fixture
async def token(client, user):
    response = client.post(
        '/login',
        data={'username': user.username, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest_asyncio.fixture
async def image_id(session, user, tmp_path) -> int:
    image_filename = f'{uuid.uuid4()}.png'
    image_path = tmp_path / image_filename
    image_path.write_bytes(b'fake image content')

    image = Image(
        filename='test_image.png',
        url=str(image_path),
        user_id=user.id,
    )
    session.add(image)
    await session.commit()
    await session.refresh(image)

    return image.id


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

    event.listen(model, 'before_insert', fake_time_hook)

    yield time

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
