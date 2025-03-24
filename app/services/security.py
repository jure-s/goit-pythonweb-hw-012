from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хешує пароль перед збереженням у БД."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє, чи введений пароль відповідає збереженому хешу."""
    return pwd_context.verify(plain_password, hashed_password)
