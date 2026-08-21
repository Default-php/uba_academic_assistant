"""Persistencia de datos scrapeados en la base de datos."""

import logging

from core.models import Evaluation, Subject

logger = logging.getLogger(__name__)


def save_subjects(entries: list[dict]) -> None:
    """Guarda o actualiza materias por codigo."""
    for m in entries:
        obj, created = Subject.objects.update_or_create(
            codigo=m["codigo"],
            defaults={"nombre": m["nombre"], "trimestre": m["trimestre"]},
        )
        logger.debug("%s: %s", "Creada" if created else "Ya existe", m["nombre"])


def save_professors(entries: list[dict]) -> None:
    """Actualiza el profesor de cada materia que coincida por codigo."""
    for entry in entries:
        try:
            subj = Subject.objects.get(codigo=entry["codigo"])
        except Subject.DoesNotExist:
            logger.warning("Materia no encontrada: %s", entry["codigo"])
            continue
        nombre = entry.get("profesor")
        if nombre:
            subj.profesor = nombre
            subj.save(update_fields=["profesor"])
            logger.debug("Profesor %s para %s", nombre, subj.nombre)


def save_evaluations(user, entries: list[dict]) -> None:
    """Borra las evaluaciones previas del usuario y guarda las nuevas."""
    Evaluation.objects.filter(user=user).delete()
    for ev in entries:
        try:
            subj = Subject.objects.get(codigo=ev["subject_codigo"])
        except Subject.DoesNotExist:
            logger.warning("Evaluación para materia desconocida: %s", ev["subject_codigo"])
            continue

        obj, created = Evaluation.objects.update_or_create(
            user=user,
            moodle_id=ev["moodle_id"],
            defaults={
                "subject": subj,
                "titulo": ev.get("titulo"),
                "url": ev.get("url"),
                "numero": ev.get("numero"),
                "unidad": ev.get("unidad"),
                "tipo": ev.get("tipo"),
                "seccion": ev.get("seccion"),
                "profesor": ev.get("profesor"),
                "porcentaje": ev.get("porcentaje"),
                "fecha_inicio": ev.get("fecha_inicio"),
                "fecha_cierre": ev.get("fecha_cierre"),
                "contenido_html": ev.get("contenido_html"),
            },
        )
        logger.debug("%s: %s", "Creada" if created else "Actualizada", ev.get("titulo"))
