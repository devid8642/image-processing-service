from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from fastapi import HTTPException, status
from jwt import decode, encode

from image_processing_service.models import User
from image_processing_service.security import (
    create_access_token,
    get_current_user,
)
from image_processing_service.settings import settings


class MockUserService:
    def __init__(self, user: User | None):
        self._user = user

    async def get_user(self, username: str):
        if self._user and self._user.username == username:
            return self._user
        return None


def fake_generate_token(username: str, expires_delta_minutes: int = 15) -> str:
    expire = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=expires_delta_minutes
    )
    payload = {'sub': username, 'exp': expire}
    return encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


@pytest.mark.asyncio
async def test_get_current_user_success():
    user = User(
        username='validuser',
        password='hashed'
    )
    token = fake_generate_token(user.username)

    user_service = MockUserService(user)
    result = await get_current_user(user_service=user_service, token=token)

    assert result.username == user.username


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    invalid_token = 'invalid.token.value'
    user_service = MockUserService(None)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(user_service=user_service, token=invalid_token)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'


@pytest.mark.asyncio
async def test_get_current_user_user_not_found():
    token = fake_generate_token('ghostuser')
    user_service = MockUserService(None)

    with pytest.raises(HTTPException) as exc:
        await get_current_user(user_service=user_service, token=token)

    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert exc.value.detail == 'Could not validate credentials'
