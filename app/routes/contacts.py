from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import crud, schemas
from app.config import SessionLocal
from app.services.utils import search_contacts, get_upcoming_birthdays
from app.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["Contacts"])

# 🔹 Функція для отримання сесії бази даних
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


# 🔹 Створення нового контакту
@router.post("/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Створення нового контакту.

    :param contact: Дані для створення контакту.
    :param db: Сесія бази даних.
    :param current_user: Поточний користувач, для якого створюється контакт.
    :return: Створений контакт.
    """
    return crud.create_contact(db, contact, current_user.id)


# 🔹 Отримання всіх контактів користувача
@router.get("/", response_model=list[schemas.ContactResponse])
def get_contacts(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Отримання всіх контактів поточного користувача.

    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Список всіх контактів користувача.
    """
    return crud.get_contacts(db, current_user.id)


# 🔹 Отримання одного контакту за ID
@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Отримання контакту за ID.

    :param contact_id: ID контакту.
    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Контакт або помилка 404, якщо контакт не знайдений.
    """
    db_contact = crud.get_contact_by_id(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


# 🔹 Оновлення контакту
@router.put("/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Оновлення даних контакту.

    :param contact_id: ID контакту.
    :param contact: Дані для оновлення контакту.
    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Оновлений контакт.
    """
    db_contact = crud.update_contact(db, contact_id, contact, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


# 🔹 Видалення контакту
@router.delete("/{contact_id}", response_model=schemas.ContactResponse)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Видалення контакту.

    :param contact_id: ID контакту для видалення.
    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Видалений контакт або помилка 404, якщо не знайдено.
    """
    db_contact = crud.delete_contact(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


# 🔹 Пошук контактів за ім'ям, прізвищем або email
@router.get("/search/", response_model=list[schemas.ContactResponse])
def search_contacts_api(
    name: str = Query(None, description="Search by first or last name"),
    email: str = Query(None, description="Search by email"),
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Пошук контактів за ім'ям, прізвищем або email.

    :param name: Ім'я або прізвище для пошуку.
    :param email: Email для пошуку.
    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Список знайдених контактів.
    """
    contacts = search_contacts(db, name, email, current_user.id)
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")
    return contacts


# 🔹 Отримання контактів з найближчими днями народження
@router.get("/upcoming_birthdays/", response_model=list[schemas.ContactResponse])
def get_birthdays_api(
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    """
    Отримання контактів з найближчими днями народження.

    :param db: Сесія бази даних.
    :param current_user: Поточний користувач.
    :return: Список контактів з найближчими днями народження.
    """
    contacts = get_upcoming_birthdays(db, current_user.id)
    if not contacts:
        raise HTTPException(status_code=404, detail="No upcoming birthdays found")
    return contacts
