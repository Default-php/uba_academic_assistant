from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.professors import scrape_professors
from core.scraping.save import save_professors
from core.utils.creds import resolve_creds


class Command(BaseCommand):
    help = "Sincroniza los nombres de los profesores para cada materia"

    def add_arguments(self, parser):
        parser.add_argument("--ci", help="Cédula de acceso al campus (o UBA_USER_CI en .env)")
        parser.add_argument(
            "--password",
            help="Contraseña de acceso al campus (o UBA_USER_PASSWD en .env; si falta, se pide)",
        )

    def handle(self, *args, **options):
        ci, password = resolve_creds(options["ci"], options["password"])

        with MoodleClient(ci, password) as client:
            client.login()
            profs = scrape_professors(client)

        save_professors(profs)
        for entry in profs:
            self.stdout.write(f"Profesor: {entry['profesor']} (ID {entry['codigo']})")

        self.stdout.write(self.style.SUCCESS("Sincronización de profesores completada."))
