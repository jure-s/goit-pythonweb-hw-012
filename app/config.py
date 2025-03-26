import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from redis import asyncio as aioredis
from fastapi_limiter import FastAPILimiter

# Завантажуємо змінні середовища
load_dotenv()

# Перевірка змінних середовища
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

# Функція для отримання URL бази даних
def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL is not set.")
    return database_url

# Отримуємо URL бази даних
SQLALCHEMY_DATABASE_URL = get_database_url()

# Отримуємо URL Redis
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Якщо змінна DATABASE_URL не була знайдена, вивести повідомлення
if SQLALCHEMY_DATABASE_URL is None:
    print("ERROR: DATABASE_URL is not set.")
else:
    print(f"Using database: {SQLALCHEMY_DATABASE_URL}")  # Додаємо вивід для перевірки

# Створюємо двигун бази даних
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Створюємо фабрику сесій
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовий клас для моделей SQLAlchemy
Base = declarative_base()

# Імпортуємо всі моделі, щоб Alembic бачив їх
from app.database import models

# Ініціалізація FastAPI Rate Limiter (обмеження запитів)
async def init_limiter():
    redis = await aioredis.from_url(REDIS_URL)
    await FastAPILimiter.init(redis)

# Шлях до папки з аватарами
AVATAR_STORAGE_PATH = os.getenv("AVATAR_STORAGE_PATH", "app/static/avatars")

# Створюємо директорію для збереження аватарів, якщо вона ще не існує
os.makedirs(AVATAR_STORAGE_PATH, exist_ok=True)
