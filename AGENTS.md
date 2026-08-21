# AGENTS.md

## Project

Django 5.2 app that scrapes the Universidad Bicentenaria de Aragua virtual
campus (Moodle) with Selenium, stores subjects/evaluations per user in
PostgreSQL, and renders a Tailwind dashboard. Background sync runs through
django-q; the API is DRF + JWT.

Target platform: Ubuntu Linux (originally Windows/XAMPP; no Windows support).

## Commands

```sh
# venv (Python 3.10, recreated for Ubuntu)
python3.10 -m venv .venv && .venv/bin/pip install -r requirements.txt

# database
.venv/bin/python manage.py migrate

# server
.venv/bin/python manage.py runserver

# tailwind watch: src/input.css -> static/css/output.css (commit the output)
npm run dev

# background sync worker — REQUIRED for POST /api/users/sync/
.venv/bin/python manage.py qcluster

# CLI sync (scrape del campus; --ci es la cédula del campus, salvo en
# sync_evaluations donde es la cédula del usuario de la app)
.venv/bin/python manage.py sync_subjects --ci <CI> [--password]
.venv/bin/python manage.py sync_professors --ci <CI> [--password]
.venv/bin/python manage.py sync_evaluations --ci <CI> [--password]

# tests / lint
.venv/bin/python manage.py test core
.venv/bin/ruff check .
.venv/bin/ruff format .
.venv/bin/ruff format --check .
```

## Architecture

- `uba_assistant/` — Django project config (`settings.py`, `urls.py`)
- `core/` — single app:
  - `models.py` — `User` (auth by cedula `ci`), `Subject`, `Inscription`,
    `Evaluation` (per-user Moodle data), `Grade`, `ConsultationResource`
  - `core/scraping/` — Moodle scraping via Selenium + requests
  - `core/view/` — dashboard/auth views; DRF API in `views.py` + `serializers.py`
  - `tasks.py` — `sync_for_user` pipeline: subjects -> professors -> evaluations
- Scraper selectors are tied to the live Moodle DOM and break when the campus
  changes. Re-verify against the live site before claiming scraping works.

## Gotchas

- django-q 1.3.9 needs the `CompatTimestampSigner` monkeypatch at the top of
  `settings.py` — never remove it.
- `Q_CLUSTER['poll'] = 0` disables the scheduler (only on-demand jobs run).
- Scrapers launch headless Chrome: `google-chrome-stable` must be installed on
  the system; chromedriver is auto-fetched by webdriver-manager.
- UBA campus credentials are held only transiently by the sync task
  (submitted from the dashboard, passed to django-q). For CLI dev use,
  `UBA_USER_CI`/`UBA_USER_PASSWD` may be set in the local `.env` (never
  committed, never logged).
- `.env` is required locally (copy `.env.example`); gitignored.
- Los features de AI (core/view/assistant.py, core/utils/openrouter_client.py,
  modelo AgentInteraction, panel de chat del dashboard) son parte del proyecto
  — no borrarlos. El chat requiere OPENROUTER_API_KEY en .env; la app arranca
  sin ella y el endpoint responde 503.
- El chat de OpenRouter necesita una `OPENROUTER_API_KEY` válida en `.env`;
  la app arranca sin ella y `/api/chat/` responde 503. El modelo gratuito por
  defecto (`meta-llama/llama-3.3-70b-instruct:free`) es sobreescribible vía
  `OPENROUTER_DEFAULT_MODEL`.
- `requirements.txt` is minimal pinned deps; add deliberately, never via
  `pip freeze` (the original file was a Windows UTF-16 freeze dump).
- Ruff config lives in `ruff.toml`; E402 is ignored in `settings.py` because
  the django-q monkeypatch must run before the rest of the imports.
- Tests must not hit the network — scraping is mocked in tests.
- UI strings, model fields and docstrings are Spanish. Keep comments brief and
  only where they add information.

## Git workflow

- Branches: `main` (releases), `develop` (integration), `feature/*` (work).
- Conventional prefixes + short subject, e.g. `Feat:`, `Refactor:`, `Chore:`,
  `Fix:`.
- Never commit: `.env`, `.venv/`, `node_modules/`, `media/`, `.opencode/`,
  `.ignore`, `__pycache__`.
- The 44-commit feature history (`feature/uba-assistant-backdev`) and the
  `feature/ubuntu-refactor` history were both merged into `main` with
  `--no-ff`; merged feature branches are deleted from origin.
