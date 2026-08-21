# PLAN.md

Refactorización completa del repo para presentarlo en GitHub como un proyecto
funcional (o "antes-funcional" si el campus cambió). Objetivo: compatibilidad
total con Ubuntu Linux, código ordenado, sin configuración de agentes en el
repo remoto.

## Decisiones tomadas

- Python 3.10 + Django 5.2 LTS (`.venv` recreado desde cero)
- PostgreSQL (instalación local en Ubuntu)
- Historia git preservada: `feature/uba-assistant-backdev` se fusiona a `main`
  con `--no-ff`; ramas feature viejas de origin se eliminan tras fusionar
- Los features de AI del proyecto se mantienen (chat del dashboard, cliente
  OpenRouter, AgentInteraction); lo que NO entra al repo remoto es la
  configuración de agentes (`.opencode/`, `.ignore`)
- Tooling: ruff (lint + format) y tests con el runner de Django
- Nomenclatura de commits: `Feat:`, `Refactor:`, `Chore:`, `Fix:` + sujeto corto
- Comentarios: breves, descriptivos, solo donde aportan; UI/modelos en español

## Roles

- **Coordinador** (yo): decisiones, docs, git, reviso AGENTS.md/PLAN.md tras
  cada fase.
- **Builder**: implementa cambios de código.
- **Critic**: revisa el código del Builder (calidad, bugs, edge cases). No
  hace commits ni merges; no revisa nombres de commits ni git.

## Fase 0 — Infraestructura local (Ubuntu)

- [x] Instalar PostgreSQL + contrib (comandos sudo: los ejecuta el usuario)
- [x] Instalar `google-chrome-stable` (comandos sudo: los ejecuta el usuario)
- [x] Recrear `.venv` con `python3.10`
- [x] Reescribir `requirements.txt`: UTF-8, deps mínimas pineadas
  (Django 5.2 LTS, DRF, simplejwt, drf-yasg, corsheaders, django-q, selenium,
  webdriver-manager, requests, beautifulsoup4, python-dotenv, psycopg[binary],
  ruff). Prohibido `pip freeze`.
- [x] `settings.py`: configuración por `.env` (SECRET_KEY, DEBUG, ALLOWED_HOSTS,
  DATABASES Postgres), fusionar el `SIMPLE_JWT` duplicado
- [x] Crear `.env.example` + `.env` local (credenciales solo locales)
- [x] Crear DB y usuario Postgres; `migrate` limpio

## Fase 1 — Consolidación git

- [x] Commit `Chore:` que saca del tracking `node_modules/` y `__pycache__`
  (`git rm -r --cached`) y arregla `.gitignore`
- [x] Tag en el tip de `feature/uba-assistant-backdev` antes de fusionar
- [x] Merge `feature/uba-assistant-backdev` → `develop` → `main` (`--no-ff`)
- [x] Eliminar ramas feature de origin ya fusionadas
- [x] Verificar que `main` contiene el trabajo completo

## Fase 2 — Configuración de agentes fuera del repo remoto

- [x] Verificar que `.opencode/` no existe ni se comitea
- [x] `.ignore` permanece local y gitignored
- [x] Ninguna config de agentes se pushea
- [x] Los features AI del proyecto permanecen intactos

## Fase 3 — Refactorización de código

- [x] Consolidar los 4 helpers de sesión/scraping duplicados en `core/scraping/`
  (cliente Moodle único + parsers)
- [x] Borrar código muerto: `core/sync/session.py`, `core/utils/sync.py`,
  `core/utils/sync_selenium.py`, `auth_views.RegisterView` duplicado
- [x] Arreglar management commands: aceptar `--ci`/`--password` y delegar al
  pipeline compartido
- [x] Modelos: `Evaluation.url` nullable, `fecha_inicio`/`fecha_cierre` como
  `DateField`, quitar campos/flag de sincronización si no se usan
- [x] Vistas/API: permisos en viewsets (nada público sin auth), un solo
  `RegisterView`, fix del filtro de fechas en `dashboard.html`
- [x] Comentarios: limpiar ruido, dejar solo lo útil (breve, descriptivo)
- [x] Tests reales: `parser_evaluations`, modelos, pipeline de sync con mocks
- [x] ruff check/format limpio; `manage.py check` limpio
- [x] Restaurar los features AI del proyecto sobre el código refactorizado
  (chat con auth, cliente OpenRouter lazy, AgentInteraction)
- [x] Cambiar el cliente OpenAI por OpenRouter con modelo gratuito
  (llama-3.3-70b-instruct:free por defecto)

## Fase 4 — Verificación en vivo

- [x] Smoke test del server: login, registro, dashboard (sin datos)
- [x] Tailwind compila y `static/css/output.css` queda comprometido
- [x] Sonda de scraping contra el campus real → pedirle al usuario sus datos
  de sesión UBA (CI + contraseña) en este momento
- [x] Adaptar selectores/flujo al DOM actual del campus; si el campus cambió
  de forma irreparable, cerrar como proyecto "antes-funcional"
- [ ] Chat en vivo con OpenRouter (pendiente: la key de OpenRouter del usuario
  no es válida — el endpoint está verificado con tests)

## Fase 5 — Publicación

- [x] `README.md` final: descripción, features, setup Ubuntu (prerequisitos,
  pasos), variables de `.env`, comandos, estructura, disclaimer del scraping
- [x] Revisión final de AGENTS.md/PLAN.md tras el último commit
- [x] Commits finales por convención y push de `main` a origin

## Resultado final

El scraping sigue funcionando contra el campus (agosto 2026) tras un fix menor
del selector de profesores; proyecto funcional.

## Notas

- Comandos que requieren `sudo` los ejecuta el usuario; yo los preparo
- Nunca loguear ni persistir credenciales UBA
- Los comandos CLI de sincronización admiten `UBA_USER_CI`/`UBA_USER_PASSWD`
  en `.env` como fallback si se omiten `--ci`/`--password` (nunca se comitean)
- Nunca comitear: `.env`, `.venv/`, `node_modules/`, `media/`, `.opencode/`,
  `.ignore`
- Después de cada fase: actualizar AGENTS.md/PLAN.md si algo cambió
