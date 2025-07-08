# core/tasks.py

import logging
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Subject, Evaluation
from core.sync.subjects import scrape_subjects
from core.sync.professors import scrape_professors
from core.sync.evaluations import scrape_evaluations

logger = logging.getLogger(__name__)
User = get_user_model()

def sync_for_user(user_id: int, ci: str, password: str):
    logger.info(f"🔄 [SYNC START] Usuario {user_id}, CI={ci}")

    try:
        user = User.objects.get(pk=user_id)

        # 1) Materias
        logger.info("   → Scrapeando materias…")
        subjects_data = scrape_subjects(ci, password)
        logger.info(f"   → Encontradas {len(subjects_data)} materias")

        for m in subjects_data:
            subj, created = Subject.objects.get_or_create(
                codigo=m["codigo"],
                defaults={
                    "nombre":    m["nombre"],
                    "trimestre": m["trimestre"]
                }
            )
            logger.debug(f"      {'Creada' if created else 'Ya existe'}: {m['nombre']}")

        # 2) Profesores
        logger.info("   → Scrapeando profesores…")
        profs_data = scrape_professors(ci, password)
        logger.info(f"   → Profesores procesados: {len(profs_data)}")

        for entry in profs_data:
            try:
                subj = Subject.objects.get(codigo=entry["codigo"])
                nombre = entry.get("profesor")
                if nombre:
                    subj.profesor = nombre
                    subj.save(update_fields=["profesor"])
                    logger.debug(f"      Profesor {nombre} para {subj.nombre}")
            except Subject.DoesNotExist:
                logger.warning(f"      Materia no encontrada: {entry['codigo']}")

        # 3) Evaluaciones
        logger.info("   → Limpiando evaluaciones previas del usuario…")
        Evaluation.objects.filter(user=user).delete()

        logger.info("   → Scrapeando evaluaciones…")
        evals_data = scrape_evaluations()
        logger.info(f"   → Encontradas {len(evals_data)} evaluaciones")

        for ev in evals_data:
            try:
                subj = Subject.objects.get(codigo=ev["subject_codigo"])
            except Subject.DoesNotExist:
                logger.warning(
                    f"      Evaluación para materia desconocida: {ev['subject_codigo']}"
                )
                continue

            obj, created = Evaluation.objects.update_or_create(
                user=user,
                moodle_id=ev["moodle_id"],
                defaults={
                    "subject":        subj,
                    "titulo":         ev.get("titulo"),
                    "numero":         ev.get("numero"),
                    "unidad":         ev.get("unidad"),
                    "tipo":           ev.get("tipo"),
                    "seccion":        ev.get("seccion"),
                    "profesor":       ev.get("profesor"),
                    "porcentaje":     ev.get("porcentaje"),
                    "fecha_inicio":   ev.get("fecha_inicio"),
                    "fecha_cierre":   ev.get("fecha_cierre"),
                    "contenido_html": ev.get("contenido_html"),
                }
            )
            logger.debug(f"      {'Creada' if created else 'Actualizada'}: {ev.get('titulo')}")

        # 4) Marca sincronizado
        user.is_synced = True
        user.last_synced = timezone.now()
        user.save()

        logger.info(f"✅ [SYNC END] Usuario {user_id} sincronizado con éxito.")

    except Exception as e:
        # Captura errores y evita reintentos
        logger.error(f"❌ [SYNC ERROR] Usuario {user_id}: {e}", exc_info=True)