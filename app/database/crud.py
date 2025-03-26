from typing import Optional
from sqlalchemy.orm import Session
from app.database.models import Contact, User
from app.database.schemas import (
    ContactCreate, ContactUpdate,
    UserCreate, UserResponse
)
from app.services.security import hash_password, verify_password as verify_password_service  # 🔹 Імпорт з одного джерела


# 🔹 Операції з користувачами (User)
def create_user(db: Session, user: UserCreate) -> UserResponse:
    """
    Створення нового користувача з хешуванням пароля.

    :param db: Сесія бази даних.
    :param user: Дані користувача для створення.
    :return: Об'єкт відповіді користувача.
    """
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return UserResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_verified=db_user.is_verified,
        avatar_url=db_user.avatar_url,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at
    )


def get_user_by_email(db: Session, email: str):
    """
    Отримання користувача за email.

    :param db: Сесія бази даних.
    :param email: Email користувача.
    :return: Користувач або None.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Отримання користувача за ID.

    :param db: Сесія бази даних.
    :param user_id: ID користувача.
    :return: Користувач або None.
    """
    return db.query(User).filter(User.id == user_id).first()


def update_avatar(db: Session, user: User, avatar_path: str):
    """
    Оновлення шляху до аватара користувача.

    :param db: Сесія бази даних.
    :param user: Користувач, якого потрібно оновити.
    :param avatar_path: Новий шлях до аватара.
    :return: Оновлений користувач.
    """
    user.avatar_url = avatar_path
    db.commit()
    db.refresh(user)
    return user


def update_user_password(db: Session, email: str, new_password: str) -> Optional[User]:
    """
    Оновлення пароля користувача за email.

    :param db: Сесія бази даних.
    :param email: Email користувача для оновлення пароля.
    :param new_password: Новий пароль.
    :return: Оновлений користувач або None.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    user.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(user)
    return user


# 🔹 Операції з контактами (Contact)
def create_contact(db: Session, contact: ContactCreate, user_id: int):
    """
    Створення нового контакту.

    :param db: Сесія бази даних.
    :param contact: Дані контакту для створення.
    :param user_id: ID користувача, якому належить контакт.
    :return: Створений контакт.
    """
    db_contact = Contact(
        **contact.model_dump(),
        user_id=user_id
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session, user_id: int):
    """
    Отримання всіх контактів користувача.

    :param db: Сесія бази даних.
    :param user_id: ID користувача, контакти якого потрібно отримати.
    :return: Список всіх контактів користувача.
    """
    return db.query(Contact).filter(Contact.user_id == user_id).all()


def get_contact_by_id(db: Session, contact_id: int, user_id: int):
    """
    Отримання контакту за ID (тільки якщо він належить користувачеві).

    :param db: Сесія бази даних.
    :param contact_id: ID контакту.
    :param user_id: ID користувача.
    :return: Контакт або None.
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()


def update_contact(db: Session, contact_id: int, contact: ContactUpdate, user_id: int):
    """
    Оновлення інформації про контакт.

    :param db: Сесія бази даних.
    :param contact_id: ID контакту для оновлення.
    :param contact: Дані для оновлення контакту.
    :param user_id: ID користувача, якому належить контакт.
    :return: Оновлений контакт.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        for key, value in contact.model_dump(exclude_unset=True).items():
            setattr(db_contact, key, value)
        db.commit()
        db.refresh(db_contact)
    return db_contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Видалення контакту.

    :param db: Сесія бази даних.
    :param contact_id: ID контакту для видалення.
    :param user_id: ID користувача, якому належить контакт.
    :return: Видалений контакт або None.
    """
    db_contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact


# 🔹 Функції для видалення користувачів (User)
def delete_user(db: Session, user_id: int):
    """
    Видалення користувача за ID.

    :param db: Сесія бази даних.
    :param user_id: ID користувача для видалення.
    :return: Видалений користувач або None.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# 🔹 Перевірка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Перевірка, чи введений пароль відповідає збереженому хешу.

    :param plain_password: Введений користувачем пароль.
    :param hashed_password: Збережений хеш пароля.
    :return: True, якщо паролі співпадають, інакше False.
    """
    return verify_password_service(plain_password, hashed_password)
