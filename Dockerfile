# Використовуємо офіційний Python 3.11
FROM python:3.11

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли проєкту
COPY . /app

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Експонуємо порт
EXPOSE 8000

# Запускаємо FastAPI додаток
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
