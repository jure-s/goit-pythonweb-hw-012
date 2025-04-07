import uuid
import pytest
from app.config import SessionLocal
from app.services.security import hash_password
from app.database.models import User
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def create_user(email: str, password: str, role: str = "user") -> None:
    """
    Створює користувача в базі даних напряму для тесту refresh токенів.
    """
    db = SessionLocal()
    hashed_password = hash_password(password)
    user = User(
        username=email.split("@")[0],
        email=email,
        password_hash=hashed_password,
        is_verified=True,
        role=role
    )
    db.add(user)
    db.commit()
    db.close()


@pytest.mark.parametrize("role", ["user", "admin"])
def test_refresh_token_flow(role):
    """
    Перевіряє логіку отримання нового access токена через refresh токен.
    """
    # Arrange
    unique = uuid.uuid4().hex[:6]
    email = f"{role}_{unique}@test.com"
    password = "TestPass123"
    create_user(email, password, role=role)

    # Login
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Refresh
    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": data["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    refresh_data = refresh_response.json()
    assert "access_token" in refresh_data
    assert refresh_data["token_type"] == "bearer"
