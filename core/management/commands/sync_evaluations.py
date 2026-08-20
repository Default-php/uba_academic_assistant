from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

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
        parser.add_argument("--password", required=True, help="Contraseña de acceso al campus")

    def handle(self, *args, **options):
        ci = options["ci"]
        password = options["password"]

        try:
            user = User.objects.get(ci=ci)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"No existe un usuario con cédula {ci}"
            ))
            return

        with MoodleClient(ci, password) as client:
            entries = scrape_evaluations(client)

        save_evaluations(user, entries)
        for ev in entries:
            self.stdout.write(
                f"Guardada: {ev['titulo']} (ID {ev['moodle_id']})"
            )

        self.stdout.write(self.style.SUCCESS(
            "Sincronización de evaluaciones completada."
        ))
