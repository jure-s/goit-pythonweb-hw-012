import io
import uuid
from tests.conftest import create_user_in_db, get_auth_header
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_avatar_upload_admin_only():
    """
    Перевіряє, що лише адміністратор може завантажити аватар.
    """
    unique = uuid.uuid4().hex[:8]
    email = f"admin_{unique}@example.com"
    password = "AdminPass123"
    create_user_in_db(email, password, role="admin")
    headers = get_auth_header(email, password)

    file_content = b"fake image content"
    files = {"file": ("avatar.png", io.BytesIO(file_content), "image/png")}

    response = client.post("/users/avatar", files=files, headers=headers)

    assert response.status_code == 200
    assert response.json()["avatar_url"].endswith(".png")

def test_avatar_upload_user_forbidden():
    """
    Перевіряє, що звичайний користувач не може завантажити аватар.
    """
    unique = uuid.uuid4().hex[:8]
    email = f"user_{unique}@example.com"
    password = "UserPass123"
    create_user_in_db(email, password, role="user")
    headers = get_auth_header(email, password)

    file_content = b"fake image content"
    files = {"file": ("avatar.png", io.BytesIO(file_content), "image/png")}

    response = client.post("/users/avatar", files=files, headers=headers)

    assert response.status_code == 403
