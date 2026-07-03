# Используем официальный образ Python
FROM python:3.12-slim AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем uv (быстрый менеджер пакетов)
RUN pip install --no-cache-dir uv

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости через uv (это быстрее и кеширует)
RUN uv pip install --system --no-cache -r requirements.txt

# ====== Второй этап: финальный образ ======
FROM python:3.12-slim

WORKDIR /app

# Копируем установленные зависимости из первого этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY app/ ./app/

# Открываем порт
EXPOSE 8000

# Запускаем uvicorn (уже установлен через uv)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]