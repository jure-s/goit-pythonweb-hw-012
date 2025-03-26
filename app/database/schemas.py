from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date

# Схема для токена
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# Схеми для користувачів (User)
class UserCreate(BaseModel):
    """Схема для створення користувача"""
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Схема відповіді для користувача"""
    id: int
    username: str
    email: EmailStr
    is_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    """Схема для логіну користувача"""
    email: EmailStr
    password: str

# Схеми для контактів (Contact)
class ContactCreate(BaseModel):
    """Схема для створення контакту"""
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: Optional[date] = None
    extra_info: Optional[str] = None

class ContactUpdate(BaseModel):
    """Схема для оновлення контакту"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    birthday: Optional[date] = None
    extra_info: Optional[str] = None

class ContactResponse(ContactCreate):
    """Схема відповіді для контакту"""
    id: int
    user_id: int

    class Config:
        orm_mode = True
