from getpass import getpass

from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.professors import scrape_professors
from core.scraping.save import save_professors


class Command(BaseCommand):
    help = "Sincroniza los nombres de los profesores para cada materia"

    def add_arguments(self, parser):
        parser.add_argument("--ci", required=True, help="Cédula de acceso al campus")
        parser.add_argument(
            "--password",
            help="Contraseña de acceso al campus (si se omite, se pide de forma segura)",
        )

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"] or getpass("Contraseña del campus: ")

        with MoodleClient(ci, password) as client:
            client.login()
            profs = scrape_professors(client)

        save_professors(profs)
        for entry in profs:
            self.stdout.write(f"Profesor: {entry['profesor']} (ID {entry['codigo']})")

        self.stdout.write(self.style.SUCCESS("Sincronización de profesores completada."))
