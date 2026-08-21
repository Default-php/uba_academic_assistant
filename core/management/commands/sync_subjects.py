from django.core.management.base import BaseCommand

from core.scraping.client import MoodleClient
from core.scraping.save import save_subjects
from core.scraping.subjects import scrape_subjects
from core.utils.creds import resolve_creds


class Command(BaseCommand):
    help = "Sincroniza las materias del portal UBA a la base de datos"

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
            materias = scrape_subjects(client)

        save_subjects(materias)
        for m in materias:
            self.stdout.write(f"Guardada: {m['nombre']} (ID {m['codigo']})")
