from django.core.management.base import BaseCommand
from django.conf import settings

from core.sync.subjects import scrape_subjects
from core.models import Subject

class Command(BaseCommand):
    help = "Sincroniza las materias del portal UBA a la base de datos"

    def handle(self, *args, **options):
        # Obtenemos credenciales desde settings (o .env cargado ahí)
        username = getattr(settings, "UBA_USERNAME", None)
        password = getattr(settings, "UBA_PASSWORD", None)
        if not username or not password:
            self.stderr.write(
                self.style.ERROR(
                    "Faltan UBA_USERNAME/UBA_PASSWORD en settings"
                )
            )
            return

        # Ejecutamos el scraper y guardamos resultados
        materias = scrape_subjects(username, password)
        for m in materias:
            obj, created = Subject.objects.get_or_create(
                codigo=m["codigo"],
                defaults={
                    "nombre":    m["nombre"],
                    "trimestre": m["trimestre"]
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✔ Guardada: {m['nombre']} (ID {m['codigo']})"
                    )
                )
            else:
                self.stdout.write(
                    f"⏩ Ya existe: {m['nombre']} (ID {m['codigo']})"
                )