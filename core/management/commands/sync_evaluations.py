from django.core.management.base import BaseCommand
from django.conf import settings

from core.sync.evaluations import scrape_evaluations
from core.models import Subject, Evaluation

class Command(BaseCommand):
    help = "Sincroniza las evaluaciones desde Moodle y descarga imágenes localmente"

    def handle(self, *args, **options):
        self.stdout.write("🔄 Iniciando sincronización de evaluaciones…")

        # Ejecuta el scraper
        entries = scrape_evaluations()

        # Persiste cada evaluación
        for ev in entries:
            # Encuentra la materia
            try:
                subj = Subject.objects.get(codigo=ev["subject_codigo"])
            except Subject.DoesNotExist:
                self.stderr.write(
                    f"⚠️  Materia no encontrada: ID {ev['subject_codigo']}"
                )
                continue

            obj, created = Evaluation.objects.update_or_create(
                moodle_id=ev["moodle_id"],
                defaults={
                    "subject":       subj,
                    "titulo":        ev["titulo"],
                    "numero":        ev["numero"],
                    "unidad":        ev["unidad"],
                    "tipo":          ev["tipo"],
                    "seccion":       ev["seccion"],
                    "profesor":      ev["profesor"],
                    "porcentaje":    ev["porcentaje"],
                    "fecha_inicio":  ev["fecha_inicio"],
                    "fecha_cierre":  ev["fecha_cierre"],
                    "contenido_html":ev["contenido_html"],
                }
            )
            status = "✔ Creada" if created else "⏩ Actualizada"
            self.stdout.write(f"{status}: {ev['titulo']} (ID {ev['moodle_id']})")

        self.stdout.write(self.style.SUCCESS(
            "✅ Sincronización de evaluaciones completada."
        ))