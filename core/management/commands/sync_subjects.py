from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.save import save_subjects
from core.scraping.subjects import scrape_subjects


class Command(BaseCommand):
    help = "Sincroniza las materias del portal UBA a la base de datos"

    def add_arguments(self, parser):
        parser.add_argument("--ci", required=True, help="Cédula de acceso al campus")
        parser.add_argument("--password", required=True, help="Contraseña de acceso al campus")

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"]

        with MoodleClient(ci, password) as client:
            materias = scrape_subjects(client)

        save_subjects(materias)
        for m in materias:
            self.stdout.write(
                f"Guardada: {m['nombre']} (ID {m['codigo']})"
            )
