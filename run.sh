#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

find_python() {
  for cmd in python3 python py; do
    if command -v "$cmd" >/dev/null 2>&1; then
      if "$cmd" -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
        echo "$cmd"
        return 0
      fi
    fi
  done
  return 1
}

PYTHON="$(find_python)" || {
  echo "Python 3.10+ is required. Install from https://www.python.org/downloads/"
  exit 1
}

echo "Using: $PYTHON"

if [[ ! -x "$ROOT/venv/bin/python" ]]; then
  echo "Creating virtual environment..."
  "$PYTHON" -m venv "$ROOT/venv"
fi

"$ROOT/venv/bin/pip" install -r "$ROOT/requirements.txt" -q

if [[ ! -f "$ROOT/.env" ]]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "Created .env (SQLite mode — no PostgreSQL needed)."
fi

echo "Preparing database..."
cd "$ROOT/backend"
"$ROOT/venv/bin/python" -m db.init_db

echo ""
echo "Starting server at http://127.0.0.1:8000/"
echo "Press Ctrl+C to stop."
echo ""

(if command -v xdg-open >/dev/null; then xdg-open "http://127.0.0.1:8000/"; elif command -v open >/dev/null; then open "http://127.0.0.1:8000/"; fi) &

exec "$ROOT/venv/bin/uvicorn" main:app --host 127.0.0.1 --port 8000
