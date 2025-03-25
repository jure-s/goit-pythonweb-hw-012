import uuid

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
    # Створимо нового користувача
    import uuid

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
