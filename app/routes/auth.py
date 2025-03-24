import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi_limiter.depends import RateLimiter  # Додаємо обмеження запитів
import shutil

from app.services.auth import (
    create_access_token,
    create_verification_token,  # Функція для створення токену верифікації
    get_current_user,
    get_db,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.database import crud, schemas
from app.services.email import send_email  # Імпорт функції відправки email
from dotenv import load_dotenv
from app.config import AVATAR_STORAGE_PATH

# Завантаження змінних середовища
load_dotenv()

# Отримуємо базовий URL для верифікації (за замовчуванням локальний)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

router = APIRouter(prefix="/auth", tags=["Auth"])

# 🔹 Ендпоїнт для логіну користувача
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not crud.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 🔹 Ендпоїнт для реєстрації користувача
@router.post("/signup", response_model=schemas.UserResponse)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Створюємо користувача
    new_user = crud.create_user(db, user_data)

    # Створюємо токен для верифікації email
    verification_token = create_verification_token(user_data.email)

    # Коректне формування посилання для верифікації
    confirmation_url = f"{BASE_URL}/auth/verify/{verification_token}"

    # Відправляємо email з посиланням для підтвердження
    subject = "Please verify your email address"
    body = f"Click the following link to verify your email: {confirmation_url}"
    send_email(subject, user_data.email, body)

    return new_user

# 🔹 Ендпоїнт для отримання поточного користувача з обмеженням запитів
@router.get("/me", response_model=schemas.UserResponse, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
def read_users_me(current_user: schemas.UserResponse = Depends(get_current_user)):
    return current_user

# 🔹 Ендпоїнт для підтвердження email
@router.get("/verify/{token}", response_model=schemas.UserResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    try:
        # Декодуємо токен
        email = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

        # Отримуємо користувача за email
        user = crud.get_user_by_email(db, email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Перевіряємо, чи вже підтверджений
        if user.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

        # Оновлюємо статус верифікації
        user.is_verified = True
        db.commit()
        db.refresh(user)

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

# 🔹 Ендпоїнт для завантаження аватара користувача
@router.post("/avatar", response_model=schemas.UserResponse)
def upload_avatar(
    file: UploadFile = File(...),
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Ендпоїнт для завантаження аватара користувача"""
    file_extension = file.filename.split(".")[-1]
    avatar_filename = f"user_{current_user.id}.{file_extension}"
    avatar_path = os.path.join(AVATAR_STORAGE_PATH, avatar_filename)

    with open(avatar_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    avatar_url = f"/static/avatars/{avatar_filename}"
    updated_user = crud.update_avatar(db, current_user, avatar_url)
    
    return updated_user