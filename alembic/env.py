import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Додаємо шлях до кореневого каталогу проєкту, щоб коректно імпортувати `config.py`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Імпортуємо змінну підключення до бази даних
from app.config import SQLALCHEMY_DATABASE_URL, Base  # Імпортуємо Base, щоб Alembic міг бачити моделі

# Отримуємо конфігурацію Alembic
config = context.config

# Встановлюємо URL бази даних у конфігурацію Alembic
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Налаштування логування Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Визначаємо метадані для автогенерації міграцій
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск міграцій у 'offline' режимі.

    У цьому режимі Alembic просто генерує SQL-скрипти без підключення до БД.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск міграцій у 'online' режимі.

    У цьому режимі Alembic підключається до БД і виконує всі необхідні зміни.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
