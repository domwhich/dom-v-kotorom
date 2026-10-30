FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт 8000 (SnapDeploy будет передавать трафик на него)
EXPOSE 8000

# Запускаем приложение через gunicorn
CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:8000", "--workers", "2"]