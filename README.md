# AXS Solutions — Website + NL Analytics Demo (v2.3.0)

Deliverable for **AXS website work**: a branded **corporate website** plus an integrated **live product demo**.

## What the client gets

| Part | URL | Description |
|------|-----|-------------|
| **AXS website** | http://127.0.0.1:8000/ | Home, About, Solutions, Contact |
| **Live demo** | http://127.0.0.1:8000/demo/ | Natural language → SQL → answers |
| **API** | http://127.0.0.1:8000/docs | OpenAPI for integrations |

## Run (Windows)

Double-click **`run.bat`**, then open **http://127.0.0.1:8000/** (website home, not only the demo).

Stop with **Ctrl+C** in the server window.

## Site map

- `/` — Home (hero, services, featured solution)
- `/about.html` — About AXS Solutions
- `/solutions.html` — Solution catalog + NL-to-SQL details
- `/contact.html` — Contact placeholders (update email before production)
- `/demo/` — Interactive analytics demo
- `/ask`, `/health`, `/examples` — Backend API

## Before production go-live

1. Replace placeholder email on **Contact** with the client’s real address.
2. Add client logo/assets under `frontend/` if provided.
3. Point domain/hosting to this app (or export static pages + host API separately).
4. Set `DB_BACKEND=postgres` in `.env` if using a production database.

## Technical stack

Python 3.10+, FastAPI, SQLite (default) or PostgreSQL, static HTML/CSS frontend.
