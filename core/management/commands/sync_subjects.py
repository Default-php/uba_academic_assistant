from getpass import getpass

from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.save import save_subjects
from core.scraping.subjects import scrape_subjects


class Command(BaseCommand):
    help = "Sincroniza las materias del portal UBA a la base de datos"

    def add_arguments(self, parser):
        parser.add_argument("--ci", required=True, help="Cédula de acceso al campus")
        parser.add_argument("--password", help="Contraseña de acceso al campus (si se omite, se pide de forma segura)")

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"] or getpass("Contraseña del campus: ")

        with MoodleClient(ci, password) as client:
            client.login()
            materias = scrape_subjects(client)

        save_subjects(materias)
        for m in materias:
            self.stdout.write(
                f"Guardada: {m['nombre']} (ID {m['codigo']})"
            )
