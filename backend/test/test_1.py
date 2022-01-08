from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_login():
    response_fail = client.post('/login', json={'username': 'string', 'password': 'not a string'})
    response_success = client.post('/login', json={'username': 'string', 'password': 'string'})
    assert response_fail.json().get('access_token') is None
    assert response_success.json().get('access_token') is not None

