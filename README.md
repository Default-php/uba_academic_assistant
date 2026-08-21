# Asistente Académico UBA

Aplicación Django que sincroniza las materias y evaluaciones del campus
virtual de la Universidad Bicentenaria de Aragua (Moodle) mediante Selenium y
las muestra en un dashboard personal, con un asistente de chat de IA gratuito
vía OpenRouter.

## Estado

Funcional, verificado contra el campus en vivo (agosto 2026).

## Características

- Registro e inicio de sesión por cédula (`ci`).
- Sincronización en segundo plano (django-q) de materias, profesores y
  evaluaciones.
- Descarga local de las imágenes de las evaluaciones.
- Dashboard Tailwind colapsable con fechas de las evaluaciones.
- Chat por evaluación con contexto (modelos gratuitos de OpenRouter).
- API REST documentada (Swagger).

## Stack

- Django 5.2
- PostgreSQL
- DRF + JWT
- django-q
- Selenium + Chrome headless
- Tailwind CSS
- OpenRouter

## Prerrequisitos

- Ubuntu Linux
- Python 3.10
- PostgreSQL 14+
- Google Chrome (`google-chrome-stable`)
- Node.js (npm)

```sh
# PostgreSQL
sudo apt install postgresql postgresql-contrib

# Google Chrome (google-chrome-stable)
# Descarga el .deb desde https://www.google.com/chrome/ e instala con:
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## Instalación

```sh
# 1. Entorno virtual
python3.10 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Configuración
cp .env.example .env
# edita .env con tus credenciales

# 3. Base de datos (crea la DB y el rol, luego edita .env)
sudo -u postgres psql -c "CREATE USER uba_user WITH PASSWORD 'uba_dev_password';"
sudo -u postgres psql -c "CREATE DATABASE uba_assistant_db OWNER uba_user;"
.venv/bin/python manage.py migrate

# 4. CSS (Tailwind)
npm ci
npm run dev   # en otra terminal; compila src/input.css -> static/css/output.css

# 5. Worker de sincronización (requerido para POST /api/users/sync/)
.venv/bin/python manage.py qcluster   # en otra terminal

# 6. Servidor
.venv/bin/python manage.py runserver
```

## Variables de entorno

| Variable | Descripción | Opcional |
| --- | --- | --- |
| `SECRET_KEY` | Clave secreta de Django | No |
| `DEBUG` | `1` en desarrollo, `0` en producción | No |
| `ALLOWED_HOSTS` | Hosts permitidos separados por coma | No |
| `DB_NAME` | Nombre de la base de datos | No |
| `DB_USER` | Usuario de PostgreSQL | No |
| `DB_PASSWORD` | Contraseña de PostgreSQL | No |
| `DB_HOST` | Host de PostgreSQL | No |
| `DB_PORT` | Puerto de PostgreSQL | No |
| `OPENROUTER_API_KEY` | Clave de OpenRouter para el chat | No (el chat responde 503 sin ella) |
| `OPENROUTER_DEFAULT_MODEL` | Modelo por defecto del chat | Sí |
| `OPENROUTER_MAX_TOKENS` | Máximo de tokens del chat | Sí |
| `UBA_USER_CI` | Cédula del campus para los comandos CLI | Sí |
| `UBA_USER_PASSWD` | Contraseña del campus para los comandos CLI | Sí |

## Uso

Flujo del dashboard: regístrate → pulsa el botón **Sincronizar Evaluaciones**
(te pide la CI y contraseña del campus) → espera el polling → revisa tus
evaluaciones → usa el chat por evaluación.

Comandos CLI de sincronización (scrape del campus; `--ci` es la cédula del
campus, salvo en `sync_evaluations` donde es la cédula del usuario de la app):

```sh
.venv/bin/python manage.py sync_subjects --ci <CI> [--password]
.venv/bin/python manage.py sync_professors --ci <CI> [--password]
.venv/bin/python manage.py sync_evaluations --ci <CI> [--password]
```

Si se omiten `--ci`/`--password`, se usan `UBA_USER_CI`/`UBA_USER_PASSWD` de
`.env`.

## API

Endpoints principales (JWT):

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/refresh/`
- `POST /api/logout/`
- `POST /api/users/sync/` y `GET /api/users/sync-status/`
- `POST /api/chat/` y `POST /api/chat/<eval_id>/`

Routers: `users`, `subjects`, `inscriptions`, `evaluations`, `grades`,
`resources`, `interactions`.

Documentación interactiva: `/swagger/`.

## Pruebas y lint

```sh
.venv/bin/python manage.py test core
.venv/bin/ruff check .
.venv/bin/ruff format .
```

## Advertencias

- Las credenciales del campus se usan solo de forma transitoria (o
  localmente en `.env` para los comandos CLI) y nunca se comparten.
- El scraping depende del DOM del campus y puede romperse si este cambia.
- Proyecto con fines académicos, no apto para producción tal cual (DEBUG por
  defecto).

## Licencia

ISC (según `package.json`).
