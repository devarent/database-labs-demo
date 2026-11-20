<div align="center">
  <img src="assets/brand-logo.svg" alt="Arya Fatthurahman" width="120" />
</div>

# Database Labs Demo

<sub>A live, deployable index for 26 hands-on database labs. FastAPI + PostgreSQL 17 + a small UI, with real reads and writes.</sub>

<p>
  <img src="https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL%2017-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL 17" />
  <img src="https://img.shields.io/badge/Runs%20in-Docker-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="MIT" />
  <a href="https://github.com/devarent/database-labs-demo/actions/workflows/ci.yml"><img src="https://github.com/devarent/database-labs-demo/actions/workflows/ci.yml/badge.svg" alt="ci" /></a>
</p>

> This is the full-stack companion to **[database-labs](https://github.com/devarent/database-labs)**. It is not a mock: the API reads and writes a real PostgreSQL 17 database, and CI runs the test suite against a PostgreSQL service plus a Docker Compose smoke test.

<p align="center">
  <img src="docs/screenshot.png" alt="Database Labs demo showing 26 engines, live stats, search, filters, and engine cards" width="960" />
</p>

## What you can do

- Browse the 26 database engines from the lab collection.
- Search by engine or category, filter by runtime, and see live counts.
- Add an engine: the form issues a real `INSERT` through the API.
- Delete an engine: a real `DELETE`, gone after a refresh.
- Hit `/healthz` to verify the app can reach PostgreSQL.
- Deploy the same image to Render, Fly.io, or a VPS.

## Stack

| Layer | Choice |
| --- | --- |
| API | FastAPI, Pydantic v2 |
| UI | Jinja2 template + vanilla JavaScript, no build step |
| Database | PostgreSQL 17 |
| ORM | SQLAlchemy 2.0 with psycopg 3 |
| Tests | pytest + FastAPI TestClient, PostgreSQL in CI |
| Container | `python:3.12-slim`, non-root user |
| CI | Tests, image build, and a Compose smoke test |

## Quickstart

```bash
git clone https://github.com/devarent/database-labs-demo.git
cd database-labs-demo
docker compose up -d --build
```

Open **http://localhost:8080**. The first start creates the `engines` table and seeds the 26 labs.

If port 8080 or 5433 is already in use, copy `.env.example` to `.env`, set `APP_PORT=8088` and `DB_PORT=5435`, then reopen the stack at `http://localhost:8088`.

```bash
docker compose logs -f app   # follow the API logs
docker compose ps            # check both containers
docker compose down -v       # stop and delete the database volume
```

The app and database publish on `127.0.0.1` only. That is deliberate: never expose a database port directly to the internet.

## Remote access

Want to use this from another country without opening a port? The collection guide covers three safe patterns:

1. **SSH tunnel or WireGuard** to a small VPS.
2. **Managed free tier** for PostgreSQL (Neon, Supabase, Aiven).
3. **Public HTTP demo** behind Caddy with TLS and basic auth.

Read **[REMOTE-ACCESS.md](https://github.com/devarent/database-labs/blob/main/REMOTE-ACCESS.md)** for commands, firewall rules, and a provider map.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Server-rendered UI |
| `GET` | `/healthz` | `SELECT 1` against PostgreSQL |
| `GET` | `/api/stats` | Totals by runtime and category |
| `GET` | `/api/engines` | List; supports `q`, `category`, `runtime` |
| `GET` | `/api/categories` | Distinct categories |
| `POST` | `/api/engines` | Insert an engine (JSON) |
| `DELETE` | `/api/engines/{id}` | Delete an engine |

Create an engine:

```bash
curl -sS -X POST http://localhost:8080/api/engines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "PostgreSQL",
    "category": "Relational",
    "runtime": "docker",
    "repo_url": "https://github.com/devarent/database-labs",
    "notes": "Primary database for this demo."
  }'
```

Validation rejects short names, unknown runtimes, and non-HTTP URLs. Duplicate names return `409`.

## Tests

Local unit run against SQLite in memory:

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements-dev.txt
pytest -q
```

Against the real PostgreSQL container:

```bash
docker compose up -d db
DATABASE_URL=postgresql+psycopg://lab:labpassword@localhost:5433/labs pytest -q
```

CI uses a PostgreSQL 17 service container and then boots the full Compose stack to curl `/healthz`, so the production path is exercised on every push.

## Deploy

| Target | How | Notes |
| --- | --- | --- |
| Render | Blueprint (`render.yaml`) | Free web + free database with a time limit |
| Fly.io | `fly launch` + `fly postgres attach` | Scale to zero when idle |
| VPS | Compose + Caddy | Full control, cheapest for always-on |
| Neon/Supabase + any host | Set `DATABASE_URL` | Good free PostgreSQL tiers |

Step-by-step instructions, secrets, backups, and a post-deploy checklist are in **[DEPLOY.md](DEPLOY.md)**.

The app accepts the `postgres://` and `postgresql://` URLs that hosts hand out and rewrites them to `postgresql+psycopg://` automatically.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://lab:labpassword@localhost:5433/labs` | Database connection |
| `POSTGRES_PASSWORD` | `labpassword` | Compose-only database password |
| `APP_PORT` | `8080` | Host port for the UI |
| `DB_PORT` | `5433` | Host port for PostgreSQL |

Copy `.env.example` to `.env` for local overrides. `.env` is git-ignored.

## Data model

```sql
CREATE TABLE engines (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(80) UNIQUE NOT NULL,
    category    VARCHAR(80) NOT NULL,
    runtime     VARCHAR(16) NOT NULL,
    repo_url    VARCHAR(300) NOT NULL,
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

The schema is created at startup with `Base.metadata.create_all`. That is intentional for a demo; a long-lived deployment should use Alembic migrations.

## Project structure

```text
database-labs-demo/
├── app/
│   ├── db.py            # engine, session, URL normalization
│   ├── main.py          # routes, lifespan, validation
│   ├── models.py        # SQLAlchemy model
│   ├── seed.py          # 26 seed rows
│   ├── static/          # CSS, JS, logo, favicon
│   └── templates/       # Jinja2 UI
├── tests/test_app.py
├── .github/workflows/ci.yml
├── docker-compose.yml
├── Dockerfile
├── render.yaml
├── fly.toml
├── DEPLOY.md
└── requirements.txt
```

## Security notes

- The credentials in `docker-compose.yml` are local development values. Change them before any shared deployment.
- The app binds to `127.0.0.1` in Compose. Use a tunnel or a TLS reverse proxy, never a raw public port.
- Never commit `.env`, platform tokens, or database URLs that contain passwords.
- The container runs as a non-root user and has a healthcheck.
- If you expose a public demo, use a read-only database user and a separate demo dataset.

## License

MIT (c) 2026 Arya Fatthurahman. See [LICENSE](LICENSE).
