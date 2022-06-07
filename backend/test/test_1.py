from turtle import st
import pytest
from fastapi.testclient import TestClient

from ..app.main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_register():
    import random
    import string
    text = 'string' + \
        "".join([random.choice(string.ascii_letters) for _ in range(20)])
    response = client.post(
        '/register', json={'username': 'string', 'password': 'string', 'mail': f"{text}@example.com"})
    data = response.json()
    assert response.status_code == 409 or data.get(
        'login') == text and data.get('password') == text


def test_login():
    response_fail = client.post(
        '/login', json={'username': 'string', 'password': 'not a string'})
    response_success = client.post(
        '/login', json={'username': 'string', 'password': 'string'})
    assert response_fail.json().get('access_token') is None
    assert response_success.json().get('access_token') is not None
