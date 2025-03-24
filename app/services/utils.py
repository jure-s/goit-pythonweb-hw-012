from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.database.models import Contact

# 🔎 Функція пошуку контактів за ім'ям, прізвищем або email
def search_contacts(db: Session, name: str = None, email: str = None):
    query = db.query(Contact)
    
    if name:
        query = query.filter(
            (Contact.first_name.ilike(f"%{name}%")) | (Contact.last_name.ilike(f"%{name}%"))
        )
    
    if email:
        query = query.filter(Contact.email == email)
    
    return query.all()

# 🎉 Фільтр: контакти з днями народження у найближчі 7 днів (ІГНОРУЄ РІК)
def get_upcoming_birthdays(db: Session, user_id: int):
    today = date.today()
    next_week = today + timedelta(days=7)

    print(f"🔎 Сьогодні: {today}")
    print(f"📅 Шукаємо дні народження з {today.day}-{today.month} до {next_week.day}-{next_week.month} (ІГНОРУЄМО РІК)")

    contacts = db.query(Contact).filter(
        Contact.user_id == user_id,  # фільтрація по user_id
        ((func.extract('month', Contact.birthday) == today.month) & (func.extract('day', Contact.birthday) >= today.day)) |
        ((func.extract('month', Contact.birthday) == next_week.month) & (func.extract('day', Contact.birthday) <= next_week.day))
    ).all()

    print(f"👀 Знайдено контактів: {len(contacts)}")
    
    return contacts
