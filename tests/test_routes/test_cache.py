import pytest
from app.services.auth import create_access_token
from app.database import crud
from app.database.schemas import UserCreate
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
import random
import string

# Створення клієнта FastAPI для тестування
client = TestClient(app)

# Фікстура для підключення до бази даних
@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Створення тестового користувача з унікальним ім'ям
@pytest.fixture(scope="module")
def test_user(db):
    # Генерація випадкового суфікса для уникнення конфлікту
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    username = f"testuser_{suffix}"
    
    # Перевірка, чи існує вже користувач з таким ім'ям
    existing_user = crud.get_user_by_email(db, "test@example.com")
    if existing_user:
        # Якщо користувач існує, видаляємо його
        crud.delete_user(db, existing_user.id)

    # Створення нового користувача
    user_data = UserCreate(
        username=username,
        email="test@example.com",
        password="TestPassword123"
    )
    user = crud.create_user(db=db, user=user_data)
    return user


@pytest.fixture(scope="module")
def auth_headers(test_user):
    # Створення фейкового JWT токену для авторизації
    token = create_access_token(data={"sub": test_user.email})
    return {"Authorization": f"Bearer {token}"}


def test_contacts_cache(auth_headers):
    """Тест для кешування контактів."""
    # Перевірка запиту на контакти
    response = client.get("/contacts/", headers=auth_headers)

    # Логування відповіді
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")

    # Перевірка статусу
    assert response.status_code == 200, f"Expected status 200, but got {response.status_code}: {response.json()}"
