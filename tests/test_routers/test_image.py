import io
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from starlette import status


def test_upload_valid_image(
    monkeypatch: pytest.MonkeyPatch, client: TestClient, token: str
):
    file_content = b'fake image content'
    file = io.BytesIO(file_content)
    file.name = 'photo.png'

    # Mock da função open para evitar salvar no disco
    mock_file = AsyncMock()
    mock_file.__aenter__.return_value.write = AsyncMock()

    monkeypatch.setattr('aiofiles.open', lambda *args, **kwargs: mock_file)

    response = client.post(
        '/images',
        files={'file': ('photo.png', file, 'image/png')},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['filename'] == 'photo.png'
    assert data['url']
    assert data['uploaded_at']
    assert 'id' in data
    assert 'user_id' in data


def test_upload_invalid_file_type(client: TestClient, token: str):
    file = io.BytesIO(b'some text pretending to be a file')
    file.name = 'document.txt'

    response = client.post(
        '/images',
        files={'file': ('document.txt', file, 'text/plain')},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Only images are allowed.'


def test_upload_fails_on_save(
    monkeypatch: pytest.MonkeyPatch, client: TestClient, token: str
):
    # Cria um mock de context manager que levanta erro ao entrar
    mock_context_manager = AsyncMock()
    mock_context_manager.__aenter__.side_effect = IOError('Disk is full')

    monkeypatch.setattr(
        'aiofiles.open', lambda *args, **kwargs: mock_context_manager
    )

    file = io.BytesIO(b'fake image content')
    file.name = 'photo.png'

    response = client.post(
        '/images',
        files={'file': ('photo.png', file, 'image/png')},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()['detail'] == 'Error while saving the image.'


def test_get_image_success(client: TestClient, token: str, image_id: int):
    response = client.get(
        f'/images/{image_id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == image_id
    assert 'filename' in data
    assert 'url' in data


def test_get_image_not_found(client: TestClient, token: str):
    response = client.get(
        '/images/999999', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Image not found'


def test_list_images_success(client: TestClient, token: str):
    response = client.get(
        '/images?page=1&limit=5', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_list_images_invalid_pagination(client: TestClient, token: str):
    response = client.get(
        '/images?page=0&limit=10', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Invalid pagination parameters'


def test_transform_image_success(
    monkeypatch: pytest.MonkeyPatch,
    client: TestClient,
    token: str,
    image_id: int,
):
    monkeypatch.setattr(
        'image_processing_service.services.image_service.apply_transformations_async.delay',
        lambda *args, **kwargs: None,
    )

    response = client.post(
        f'/images/{image_id}/transform',
        json={'rotate': 90, 'format': 'png'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'filename' in data
    assert data['original_image_id'] == image_id


def test_transform_image_not_found(client: TestClient, token: str):
    response = client.post(
        '/images/999999/transform',
        json={'rotate': 45},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Image not found'


def test_transform_image_invalid_data(
    client: TestClient, token: str, image_id: int
):
    response = client.post(
        f'/images/{image_id}/transform',
        json={'rotate': 'not_a_number'},
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
