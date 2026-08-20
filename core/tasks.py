# core/tasks.py

import logging
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.scraping.client import MoodleClient
from core.scraping.evaluations import scrape_evaluations
from core.scraping.professors import scrape_professors
from core.scraping.save import save_evaluations, save_professors, save_subjects
from core.scraping.subjects import scrape_subjects

logger = logging.getLogger(__name__)
User = get_user_model()

def sync_for_user(user_id: int, ci: str, password: str):
    # 1) Obtener usuario o abortar
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error("[SYNC ERROR] Usuario %s no existe.", user_id)
        return

    # 2) Guard: si ya está sincronizado, cortamos
    if user.is_synced:
        logger.info("[SYNC SKIP] Usuario %s ya sincronizado.", user_id)
        return

    logger.info("[SYNC START] Usuario %s, CI=%s", user_id, ci)
    try:
        with MoodleClient(ci, password) as client:
            client.login()

            # 3) Scrape Materias
            logger.info("Scrapeando materias...")
            subjects_data = scrape_subjects(client)
            logger.info("Encontradas %s materias", len(subjects_data))
            save_subjects(subjects_data)

            # 4) Scrape Profesores
            logger.info("Scrapeando profesores...")
            profs_data = scrape_professors(client)
            logger.info("Profesores procesados: %s", len(profs_data))
            save_professors(profs_data)

            # 5) Scrape Evaluaciones
            logger.info("Scrapeando evaluaciones...")
            evals_data = scrape_evaluations(client)
            logger.info("Encontradas %s evaluaciones", len(evals_data))
            save_evaluations(user, evals_data)

        # 6) Marcar sincronización completa
        user.is_synced   = True
        user.last_synced = timezone.now()
        user.save(update_fields=['is_synced', 'last_synced'])
        logger.info("[SYNC END] Usuario %s sincronizado con éxito.", user_id)

    except Exception as e:
        logger.error("[SYNC ERROR] Usuario %s: %s", user_id, e, exc_info=True)
