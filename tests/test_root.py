from http import HTTPStatus

from fastapi.testclient import TestClient

from image_processing_service.main import app


def test_root():
    client = TestClient(app)

    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World!'}
