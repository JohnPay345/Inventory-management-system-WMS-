#!/bin/bash

set -euo pipefail

MAX_RETRIES=10
RETRY_INTERVAL=2

attempt=0
while ! pg_isready -h postgres -U pg_init -d management_system; do
  attempt=$((attempt + 1))
  if [ "$attempt" -ge "$MAX_RETRIES" ]; then
    echo "Превышен лимит попыток ожидания БД. Проверьте, что сервис postgres запущен и доступен."
    exit 1
  fi
  echo "БД ещё не готова (попытка $attempt/$MAX_RETRIES), жду ${RETRY_INTERVAL} сек..."
  sleep "$RETRY_INTERVAL"
done

echo "Применяем миграции Alembic..."
uv run alembic upgrade head

echo "Миграции применены. Запускаем приложение..."
exec uvicorn app:app --host 0.0.0.0 --port 8000