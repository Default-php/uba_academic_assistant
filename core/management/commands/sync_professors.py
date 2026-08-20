from django.core.management.base import BaseCommand
from django.conf import settings

from core.sync.professors import scrape_professors
from core.models import Subject

class Command(BaseCommand):
    help = "Sincroniza los nombres de los profesores para cada materia"

    def handle(self, *args, **options):
        # Credenciales desde settings (o .env cargado ahí)
        username = getattr(settings, "UBA_USERNAME", None)
        password = getattr(settings, "UBA_PASSWORD", None)
        if not username or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Error: faltan UBA_USERNAME/UBA_PASSWORD en settings"
                )
            )
            return

        # Ejecutar scraper y actualizar cada Subject
        profs = scrape_professors(username, password)
        for entry in profs:
            codigo   = entry["codigo"]
            profesor = entry["profesor"]

            try:
                subj = Subject.objects.get(codigo=codigo)
            except Subject.DoesNotExist:
                self.stderr.write(
                    self.style.WARNING(
                        f"⚠️  Materia no encontrada en BD: ID {codigo}"
                    )
                )
                continue

            # Solo guardar si encontramos un nombre válido
            if profesor:
                subj.profesor = profesor
                subj.save(update_fields=["profesor"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✔ Profesor actualizado: {subj.nombre} → {profesor}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Sin profesor para: {subj.nombre} (ID {codigo})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS("Sincronización de profesores completada.")
        )