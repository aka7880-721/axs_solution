# Multi-Agent RAG NL-to-SQL (v2.1.0)

Ask questions in plain English; the app generates SQL, queries the database, and returns an answer.

**Runs on any PC with Python 3.10+** — default **SQLite** (no PostgreSQL install). Optional PostgreSQL via `.env`.

## Easiest way to run

### Windows

Double-click **`run.bat`** or in PowerShell:

```powershell
.\run.ps1
```

### macOS / Linux

```bash
chmod +x run.sh
./run.sh
```

The script will:

1. Create a virtual environment (first run)
2. Install Python packages
3. Create `.env` from `.env.example` if missing
4. Create and seed the SQLite database
5. Open http://127.0.0.1:8000/ in your browser
6. Start the API and web UI

Stop the server with **Ctrl+C**.

## Manual run

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd backend
python -m db.init_db
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000/

## Configuration (`.env`)

| Variable | Default | Meaning |
|----------|---------|---------|
| `DB_BACKEND` | `sqlite` | `sqlite` or `postgres` |
| `SQLITE_PATH` | `data/ragdb.sqlite` | SQLite file path |
| `DB_*` | — | PostgreSQL settings when `DB_BACKEND=postgres` |

## API

- **UI:** http://127.0.0.1:8000/
- **Health:** GET `/health`
- **Ask:** POST `/ask` with `{"question": "List all customers"}`
- **Docs:** http://127.0.0.1:8000/docs

## v2.1.0

- Portable **SQLite** by default
- Auto database init on startup
- Frontend served from the same server (no `file://` issues)
- **`run.bat` / `run.ps1` / `run.sh`** one-click launchers
