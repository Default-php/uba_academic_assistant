from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from core.scraping.client import MoodleClient
from core.scraping.evaluations import scrape_evaluations
from core.scraping.save import save_evaluations
from core.utils.creds import resolve_creds

User = get_user_model()


class Command(BaseCommand):
    help = "Sincroniza las evaluaciones desde Moodle y descarga imágenes localmente"

    def add_arguments(self, parser):
        parser.add_argument(
            "--ci",
            help="Cédula del usuario de la app (o UBA_USER_CI en .env; también login del campus)",
        )
        parser.add_argument(
            "--password",
            help="Contraseña de acceso al campus (o UBA_USER_PASSWD en .env; si falta, se pide)",
        )

    def handle(self, *args, **options):
        ci, password = resolve_creds(options["ci"], options["password"])

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
