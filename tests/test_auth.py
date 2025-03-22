from http import HTTPStatus

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from image_processing_service.schemas.user_schemas import UserCreateSchema
from image_processing_service.services.user_service import get_user_service


@pytest.mark.asyncio
async def test_register_success(client: TestClient, session: AsyncSession):
    user_data = {'username': 'newuser', 'password': 'password123'}
    response = client.post('/register', json=user_data)

    assert response.status_code == HTTPStatus.CREATED
    assert 'access_token' in response.json()
    assert response.json()['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_register_username_exists(
    client: TestClient, session: AsyncSession
):
    user_service = get_user_service(session)
    existing_user = UserCreateSchema(
        username='existinguser', password='password123'
    )
    await user_service.create_user(existing_user)

    user_data = {'username': 'existinguser', 'password': 'password123'}
    response = client.post('/register', json=user_data)

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already exists'}
