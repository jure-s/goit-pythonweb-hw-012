# 📞 Contacts API (FastAPI + PostgreSQL + Docker + Auth + Redis + Email)

## 📌 Опис проєкту
Цей проєкт — повноцінний **REST API** для керування контактами з повною підтримкою:
- ✅ CRUD контактів
- 🔐 JWT аутентифікації (access + refresh токени)
- 📧 Email-підтвердження реєстрації
- 📸 Завантаження аватарів (admin only)
- 🔍 Пошук контактів
- 🎂 Дні народження
- 🧵 Кешування Redis для контактів
- 🧪 Тестування `pytest`
- 🐳 Docker-підтримка
- 📄 Swagger / Redoc

---

## ⚙️ Встановлення та запуск

### 🔹 1️⃣ Клонування репозиторію
```bash
git clone https://github.com/jure-s/goit-pythonweb-hw-012.git
cd goit-pythonweb-hw-012
```

### 🔹 2️⃣ Віртуальне середовище
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# або
source venv/bin/activate  # Linux/macOS
```

### 🔹 3️⃣ Залежності
```bash
pip install -r requirements.txt
```

### 🔹 4️⃣ .env конфігурація
Створи файл `.env` у корені з таким вмістом:

```
DATABASE_URL=postgresql://postgres:your_pass@localhost:5433/contacts_db
SECRET_KEY=your_secret_key
BASE_URL=http://127.0.0.1:8000
MAILGUN_API_KEY=your_key
MAILGUN_DOMAIN=your_domain
MAILGUN_SENDER=you@your_domain.com
REDIS_URL=redis://localhost:6379
AVATAR_STORAGE_PATH=app/static/avatars
```

---

## 🐳 Docker
```bash
docker-compose up --build
```

> Порти: FastAPI (8000), PostgreSQL (5433), Redis (6379)

---

## 📘 Swagger / Redoc
- [http://localhost:8000/docs](http://localhost:8000/docs)
- [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🔐 Аутентифікація

### POST /auth/signup
```json
{
  "username": "jure",
  "email": "jure@example.com",
  "password": "StrongPass123"
}
```

📩 Email підтвердження прийде на вказану пошту.

### POST /auth/login (`x-www-form-urlencoded`)
```
username=jure@example.com
password=StrongPass123
```

📥 Повертає:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

### POST /auth/refresh
```json
{
  "refresh_token": "тут токен"
}
```

---

## 👤 Користувачі

- `GET /auth/me` — профіль (rate-limit: 5/хв)
- `POST /auth/avatar` — лише адміністратор
- `POST /users/reset_password_request/`
- `POST /users/reset_password/`

---

## 👥 Контакти

- `POST /contacts/`
- `GET /contacts/`
- `GET /contacts/{id}`
- `PUT /contacts/{id}`
- `DELETE /contacts/{id}`
- `GET /contacts/search/?name=...&email=...` (кешується)
- `GET /contacts/upcoming_birthdays/` (кешується)

---

## 🧪 Тестування
```bash
pytest -v
```

> Покриття тестами:
- Аутентифікація
- Ролі
- CRUD контактів
- Кешування
- Email
- Refresh токени
- Валідація

---

## 📁 Структура проєкту
```
app/
├── main.py
├── config.py
├── routes/
├── database/
├── services/
├── static/avatars/
tests/
├── test_routes/
├── test_services/
├── test_database/
```

---

## 🛡️ Безпека
- `bcrypt` хешування паролів
- JWT токени (access + refresh)
- Pydantic валідація
- CORS обмеження
- Авторизація за ролями (user / admin)

---

## 📬 Email
- Mailgun API для підтвердження email і скидання пароля
- Підтримка dev/test середовища

---

## 🏁 Завершення
Проєкт демонструє повний цикл розробки API з високим рівнем безпеки, розширюваністю і надійністю.

> 💡 Створено в рамках GoIT Python Web курс — [goit-pythonweb-hw-012]