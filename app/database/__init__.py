from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_database_url

# Створення підключення до БД
DATABASE_URL = get_database_url()

# Створення сесії
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
