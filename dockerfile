# Используем официальный образ Python
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Устанавливаем рабочую директорию
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN python --version && which python && uv --version

# Копируем файл зависимостей и устанавливаем их
RUN uv self update


# Копируем код приложения
COPY . .

# Определяем команду запуска
CMD ["uv", "run", "main.py"]