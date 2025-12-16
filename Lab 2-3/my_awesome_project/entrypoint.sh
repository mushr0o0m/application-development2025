#!/bin/sh
set -e

if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Waiting for DB $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do sleep 0.1; done
fi

if [ -f "alembic.ini" ]; then
  echo "Applying alembic migrations..."
  alembic upgrade head || true
fi

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"

exec python -m uvicorn main:app --host "$HOST" --port "$PORT" --log-level "$LOG_LEVEL" --reload