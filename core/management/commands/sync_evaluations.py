from getpass import getpass

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.scraping.client import MoodleClient
from core.scraping.evaluations import scrape_evaluations
from core.scraping.save import save_evaluations

User = get_user_model()


class Command(BaseCommand):
    help = "Sincroniza las evaluaciones desde Moodle y descarga imágenes localmente"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ci",
            required=True,
            help="Cédula del usuario de la app (también usada como login del campus)",
        )
        parser.add_argument(
            "--password",
            help="Contraseña de acceso al campus (si se omite, se pide de forma segura)",
        )

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"] or getpass("Contraseña del campus: ")

        try:
            user = User.objects.get(ci=ci)
        except User.DoesNotExist:
            raise CommandError(f"No existe un usuario con cédula {ci}")

        with MoodleClient(ci, password) as client:
            client.login()
            entries = scrape_evaluations(client)

        save_evaluations(user, entries)
        for ev in entries:
            self.stdout.write(f"Guardada: {ev['titulo']} (ID {ev['moodle_id']})")

        self.stdout.write(self.style.SUCCESS("Sincronización de evaluaciones completada."))
