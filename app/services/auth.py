import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from passlib.context import CryptContext

from app.config import SessionLocal
from app.database import crud
from app.database.models import User

# Завантажуємо змінні середовища
load_dotenv()

# Конфігурація JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хешування паролів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Ініціалізація схеми аутентифікації OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Функція для отримання сесії бази даних
def get_db():
    """
    Генератор сесії для роботи з базою даних.

    :return: Сесія бази даних.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔹 Аутентифікація користувача за email та паролем
def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Аутентифікація користувача за email та паролем.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :param password: Пароль користувача.
    :return: Користувач або None, якщо аутентифікація не вдалася.
    """
    user = crud.get_user_by_email(db, email)
    if not user:
        return None
    if not pwd_context.verify(password, user.password_hash):
        return None
    return user


# 🔹 Створення JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Створення JWT токена доступу.

    :param data: Дані, які повинні бути включені в токен.
    :param expires_delta: Час до завершення терміну дії токена.
    :return: Створений токен доступу.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔹 Отримання поточного користувача за токеном
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Отримання поточного користувача за JWT токеном.

    :param token: Токен доступу.
    :param db: Сесія бази даних.
    :return: Поточний користувач.
    :raises HTTPException: Якщо токен некоректний або користувач не знайдений.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, user_email)
    if user is None:
        raise credentials_exception
    return user


# 🔹 Створення токена для підтвердження email
def create_verification_token(email: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    Створення токена для підтвердження email.

    :param email: Email користувача для підтвердження.
    :param expires_delta: Час до завершення терміну дії токена.
    :return: Створений токен для підтвердження.
    """
    to_encode = {"sub": email}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# 🔐 Генерація токена для скидання пароля
def create_reset_token(email: str, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    Генерація токена для скидання пароля.

    :param email: Email користувача для скидання пароля.
    :param expires_delta: Час до завершення терміну дії токена.
    :return: Створений токен для скидання пароля.
    """
    to_encode = {"sub": email, "scope": "reset_password"}
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ✅ Перевірка токена та витяг email
def verify_reset_token(token: str) -> Optional[str]:
    """
    Перевірка токена для скидання пароля та витягнення email користувача.

    :param token: Токен для скидання пароля.
    :return: Email користувача або None, якщо токен некоректний.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("scope") != "reset_password":
            return None
        return payload.get("sub")
    except JWTError:
        return None
