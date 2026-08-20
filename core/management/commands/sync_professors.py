from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.professors import scrape_professors
from core.scraping.save import save_professors


class Command(BaseCommand):
    help = "Sincroniza los nombres de los profesores para cada materia"

    def add_arguments(self, parser):
        parser.add_argument("--ci", required=True, help="Cédula de acceso al campus")
        parser.add_argument("--password", required=True, help="Contraseña de acceso al campus")

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"]

        with MoodleClient(ci, password) as client:
            profs = scrape_professors(client)

        save_professors(profs)
        for entry in profs:
            self.stdout.write(
                f"Profesor: {entry['profesor']} (ID {entry['codigo']})"
            )

        self.stdout.write(self.style.SUCCESS(
            "Sincronización de profesores completada."
        ))
