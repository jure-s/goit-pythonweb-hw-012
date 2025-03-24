import os
import requests
from dotenv import load_dotenv

# Завантажуємо змінні середовища з .env
load_dotenv()

MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
MAILGUN_SENDER = os.getenv("MAILGUN_SENDER")

def send_email(subject: str, to_email: str, body: str):
    """
    Надсилає email за допомогою Mailgun API.
    """
    if not MAILGUN_API_KEY or not MAILGUN_DOMAIN or not MAILGUN_SENDER:
        raise ValueError("Mailgun API Key, Domain або Sender Email не налаштовані")

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"
    auth = ("api", MAILGUN_API_KEY)
    data = {
        "from": f"Admin <{MAILGUN_SENDER}>",
        "to": [to_email],
        "subject": subject,
        "text": body
    }

    response = requests.post(url, auth=auth, data=data)

    if response.status_code == 200:
        print(f"✅ Email успішно надіслано на {to_email}")
    else:
        print(f"❌ Помилка відправлення email: {response.status_code}, {response.text}")
