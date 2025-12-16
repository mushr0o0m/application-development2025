#!/usr/bin/env zsh
set -euo pipefail

# Последовательный запуск pytest по каждому файлу в папке tests/
# Скрипт сортирует список файлов и запускает pytest для каждого по очереди.

ROOT_DIR=$(dirname "$0")
cd "$ROOT_DIR"

echo "Запуск тестов по очереди из папки: $ROOT_DIR/tests"

files=(tests/*.py)

if [ ${#files[@]} -eq 0 ]; then
  echo "Файлы тестов не найдены в tests/"
  exit 1
fi

# Отсортируем список файлов для детерминированного порядка
IFS=$'\n'
files=( $(printf "%s\n" "${files[@]}" | sort) )

for f in "${files[@]}"; do
  echo "\n=== Running: $f ==="
  pytest -q "$f"
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "Тесты упали в файле: $f (exit code $rc)"
    exit $rc
  fi
done

echo "\nВсе тесты прошли успешно."
