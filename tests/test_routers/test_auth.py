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


@pytest.mark.asyncio
async def test_login_success(client: TestClient, session: AsyncSession):
    user_service = get_user_service(session)
    user_data = UserCreateSchema(username='testuser', password='testpass123')
    await user_service.create_user(user_data)

    response = client.post(
        '/login',
        data={
            'username': user_data.username,
            'password': user_data.password,
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


@pytest.mark.asyncio
async def test_login_user_not_found(client: TestClient):
    response = client.post(
        '/login',
        data={
            'username': 'nonexistent',
            'password': 'doesntmatter',
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient, session: AsyncSession):
    user_service = get_user_service(session)
    user_data = UserCreateSchema(username='validuser', password='rightpass')
    await user_service.create_user(user_data)

    response = client.post(
        '/login',
        data={
            'username': 'validuser',
            'password': 'wrongpass',
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}
