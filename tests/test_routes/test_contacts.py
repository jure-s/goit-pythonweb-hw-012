import uuid
from datetime import date


def register_and_login_user(test_client):
    """Реєстрація та логін користувача. Повертає headers для авторизації."""
    username = f"user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"

    test_client.post("/users/signup/", json={
        "username": username,
        "email": email,
        "password": password
    })

    response = test_client.post("/users/login/", data={
        "username": email,
        "password": password
    })

    assert response.status_code == 200
    token = response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    return headers


def create_contact(test_client, headers, **overrides):
    """Створює контакт з можливістю перевизначити дані."""
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john_{uuid.uuid4().hex[:5]}@example.com",
        "phone": "1234567890"
    }
    data.update(overrides)
    response = test_client.post("/contacts/", json=data, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_create_contact(test_client):
    headers = register_and_login_user(test_client)
    contact = create_contact(test_client, headers)
    assert contact["first_name"] == "John"


def test_get_contacts(test_client):
    headers = register_and_login_user(test_client)
    contact = create_contact(test_client, headers)
    response = test_client.get("/contacts/", headers=headers)
    assert response.status_code == 200
    contacts = response.json()
    assert isinstance(contacts, list)
    assert any(c["email"] == contact["email"] for c in contacts)


def test_update_contact(test_client):
    headers = register_and_login_user(test_client)
    contact = create_contact(test_client, headers)

    updated_data = {
        "first_name": "Updated",
        "last_name": contact["last_name"],
        "email": contact["email"],
        "phone": "999888777"
    }
    response = test_client.put(f"/contacts/{contact['id']}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"
    assert response.json()["phone"] == "999888777"


def test_delete_contact(test_client):
    headers = register_and_login_user(test_client)
    contact = create_contact(test_client, headers)

    response = test_client.delete(f"/contacts/{contact['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == contact["id"]

    # Перевірка, що контакт видалено
    get_response = test_client.get(f"/contacts/{contact['id']}", headers=headers)
    assert get_response.status_code == 404


def test_get_contact_by_id(test_client):
    headers = register_and_login_user(test_client)
    contact = create_contact(test_client, headers)

    response = test_client.get(f"/contacts/{contact['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == contact["email"]


def test_search_contacts(test_client):
    headers = register_and_login_user(test_client)
    create_contact(test_client, headers, first_name="Searchable", last_name="Contact")

    response = test_client.get("/contacts/search/?name=Searchable", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert any(c["first_name"] == "Searchable" for c in results)


def test_get_upcoming_birthdays(test_client):
    headers = register_and_login_user(test_client)
    today_str = date.today().strftime("%Y-%m-%d")

    create_contact(test_client, headers, first_name="Birthday", birthday=today_str)

    response = test_client.get("/contacts/upcoming_birthdays/", headers=headers)
    assert response.status_code == 200
    results = response.json()
    assert any(c["first_name"] == "Birthday" for c in results)
