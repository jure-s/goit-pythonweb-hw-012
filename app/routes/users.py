from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.config import SessionLocal
import app.database.schemas as schemas
import app.database.crud as crud


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


# 🔹 Отримання всіх користувачів (тільки для перевірки)
@router.get("/")
def get_users():
    return {"message": "Users API is working!"}
