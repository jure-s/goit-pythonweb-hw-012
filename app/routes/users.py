from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.config import SessionLocal
import app.database.schemas as schemas
import app.database.crud as crud
from app.services.auth import authenticate_user, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

# Функція для отримання сесії БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔹 Реєстрація нового користувача
print("✅ USERS ROUTER LOADED")
print("✅ ROUTE /users/signup/ should be registered")

@router.post("/signup", response_model=schemas.UserResponse, status_code=201)
def signup(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача"""
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    new_user = crud.create_user(db, user_data)
    return new_user

# 🔹 Авторизація користувача (логін)
@router.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Авторизація користувача"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=1)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 🔹 Отримання всіх користувачів (тільки для перевірки)
@router.get("/")
def get_users():
    return {"message": "Users API is working!"}
