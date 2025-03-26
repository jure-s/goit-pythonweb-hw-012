import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def new_user_data():
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"user_{unique_id}",
        "email": f"user_{unique_id}@example.com",
        "password": "TestPassword123"
    }

def test_user_signup(client, new_user_data):
    response = client.post("/auth/signup", json=new_user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_user_data["email"]
    assert data["username"] == new_user_data["username"]
    assert "id" in data

def test_user_signup_existing_email(client, new_user_data):
    response = client.post("/auth/signup", json=new_user_data)
    assert response.status_code == 200

    response = client.post("/auth/signup", json=new_user_data)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

def test_user_login(client, new_user_data):
    client.post("/auth/signup", json=new_user_data)

    response = client.post("/auth/login", data={
        "username": new_user_data["email"],
        "password": new_user_data["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_user_login_wrong_password(client, new_user_data):
    client.post("/auth/signup", json=new_user_data)

    response = client.post("/auth/login", data={
        "username": new_user_data["email"],
        "password": "WrongPassword"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_get_current_user(client, new_user_data):
    client.post("/auth/signup", json=new_user_data)

    login_response = client.post("/auth/login", data={
        "username": new_user_data["email"],
        "password": new_user_data["password"]
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == new_user_data["email"]
