import uuid
from app.services.auth import create_reset_token  # Для тесту з реальним токеном

def test_signup_user(test_client):
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    unique_email = f"{unique_username}@example.com"

    response = test_client.post("/users/signup/", json={
        "username": unique_username,
        "email": unique_email,
        "password": "testpassword123"
    })
    assert response.status_code == 201
    assert "email" in response.json()


def test_login_user(test_client):
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    unique_email = f"{unique_username}@example.com"
    password = "testpassword123"

    # Реєстрація
    signup_response = test_client.post("/users/signup/", json={
        "username": unique_username,
        "email": unique_email,
        "password": password
    })
    assert signup_response.status_code == 201

    # Логін
    login_response = test_client.post("/users/login/", data={
        "username": unique_email,
        "password": password
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_reset_password_flow(test_client):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "initialPassword123"

    # Крок 1: Реєстрація
    signup_response = test_client.post("/users/signup/", json={
        "username": "resetuser",
        "email": unique_email,
        "password": password
    })
    assert signup_response.status_code == 201

    # Крок 2: Запит на скидання пароля
    reset_request = test_client.post("/users/reset_password_request/", params={"email": unique_email})
    assert reset_request.status_code == 200

    # ⚠️ Генеруємо токен вручну (як у сервісі)
    token = create_reset_token(unique_email)

    # Крок 3: Скидання пароля
    new_password = "newSecurePassword123"
    reset_response = test_client.post("/users/reset_password/", params={
        "token": token,
        "new_password": new_password
    })
    assert reset_response.status_code == 200
    assert "Password has been reset" in reset_response.json()["message"]

    # Крок 4: Логін з новим паролем
    login_response = test_client.post("/users/login", data={
        "username": unique_email,
        "password": new_password
    })
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_reset_password_invalid_token(test_client):
    response = test_client.post("/users/reset_password/", params={
        "token": "invalidtoken123",
        "new_password": "whatever"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"
