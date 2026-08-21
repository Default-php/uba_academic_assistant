"""Tests de comandos CLI sync_subjects, sync_professors y sync_evaluations."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

User = get_user_model()

CI = "111"
PASSWORD = "secreta"


def _client(mock_client):
    """Devuelve el cliente que entrega el context manager del MoodleClient mockeado."""
    return mock_client.return_value.__enter__.return_value


class SyncSubjectsCommandTests(TestCase):
    """sync_subjects resuelve credenciales y scrapea materias."""

    @patch("core.management.commands.sync_subjects.save_subjects")
    @patch("core.management.commands.sync_subjects.MoodleClient")
    @patch("core.management.commands.sync_subjects.scrape_subjects", return_value=[])
    def test_con_argumentos_pasa_credenciales_al_cliente(self, mock_scrape, mock_client, mock_save):
        call_command("sync_subjects", ci=CI, password=PASSWORD)

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with([])

    @patch.dict("os.environ", {"UBA_USER_CI": CI, "UBA_USER_PASSWD": PASSWORD})
    @patch("core.management.commands.sync_subjects.save_subjects")
    @patch("core.management.commands.sync_subjects.MoodleClient")
    @patch("core.management.commands.sync_subjects.scrape_subjects", return_value=[])
    def test_sin_argumentos_usa_env(self, mock_scrape, mock_client, mock_save):
        call_command("sync_subjects")

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with([])

    @patch.dict("os.environ", {}, clear=True)
    @patch("core.utils.creds.getpass", side_effect=RuntimeError("no debe pedir password"))
    @patch("core.management.commands.sync_subjects.MoodleClient")
    @patch("core.management.commands.sync_subjects.scrape_subjects")
    def test_sin_ci_lanza_command_error_sin_scrapear(self, mock_scrape, mock_client, mock_getpass):
        with self.assertRaises(CommandError):
            call_command("sync_subjects")

        mock_client.assert_not_called()
        mock_scrape.assert_not_called()
        mock_getpass.assert_not_called()


class SyncProfessorsCommandTests(TestCase):
    """sync_professors resuelve credenciales y scrapea profesores."""

    @patch("core.management.commands.sync_professors.save_professors")
    @patch("core.management.commands.sync_professors.MoodleClient")
    @patch("core.management.commands.sync_professors.scrape_professors", return_value=[])
    def test_con_argumentos_pasa_credenciales_al_cliente(self, mock_scrape, mock_client, mock_save):
        call_command("sync_professors", ci=CI, password=PASSWORD)

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with([])

    @patch.dict("os.environ", {"UBA_USER_CI": CI, "UBA_USER_PASSWD": PASSWORD})
    @patch("core.management.commands.sync_professors.save_professors")
    @patch("core.management.commands.sync_professors.MoodleClient")
    @patch("core.management.commands.sync_professors.scrape_professors", return_value=[])
    def test_sin_argumentos_usa_env(self, mock_scrape, mock_client, mock_save):
        call_command("sync_professors")

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with([])

    @patch.dict("os.environ", {}, clear=True)
    @patch("core.utils.creds.getpass", side_effect=RuntimeError("no debe pedir password"))
    @patch("core.management.commands.sync_professors.MoodleClient")
    @patch("core.management.commands.sync_professors.scrape_professors")
    def test_sin_ci_lanza_command_error_sin_scrapear(self, mock_scrape, mock_client, mock_getpass):
        with self.assertRaises(CommandError):
            call_command("sync_professors")

        mock_client.assert_not_called()
        mock_scrape.assert_not_called()
        mock_getpass.assert_not_called()


class SyncEvaluationsCommandTests(TestCase):
    """sync_evaluations resuelve credenciales, busca el usuario y scrapea."""

    def setUp(self):
        self.user = User.objects.create_user(ci=CI, nombre_completo="Ana", correo="ana@example.com")

    @patch("core.management.commands.sync_evaluations.save_evaluations")
    @patch("core.management.commands.sync_evaluations.MoodleClient")
    @patch("core.management.commands.sync_evaluations.scrape_evaluations", return_value=[])
    def test_con_argumentos_pasa_credenciales_y_usuario(self, mock_scrape, mock_client, mock_save):
        call_command("sync_evaluations", ci=CI, password=PASSWORD)

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with(self.user, [])

    @patch.dict("os.environ", {"UBA_USER_CI": CI, "UBA_USER_PASSWD": PASSWORD})
    @patch("core.management.commands.sync_evaluations.save_evaluations")
    @patch("core.management.commands.sync_evaluations.MoodleClient")
    @patch("core.management.commands.sync_evaluations.scrape_evaluations", return_value=[])
    def test_sin_argumentos_usa_env(self, mock_scrape, mock_client, mock_save):
        call_command("sync_evaluations")

        mock_client.assert_called_once_with(CI, PASSWORD)
        mock_scrape.assert_called_once_with(_client(mock_client))
        mock_save.assert_called_once_with(self.user, [])

    @patch.dict("os.environ", {}, clear=True)
    @patch("core.utils.creds.getpass", side_effect=RuntimeError("no debe pedir password"))
    @patch("core.management.commands.sync_evaluations.MoodleClient")
    @patch("core.management.commands.sync_evaluations.scrape_evaluations")
    def test_sin_ci_lanza_command_error_sin_scrapear(self, mock_scrape, mock_client, mock_getpass):
        with self.assertRaises(CommandError):
            call_command("sync_evaluations")

        mock_client.assert_not_called()
        mock_scrape.assert_not_called()
        mock_getpass.assert_not_called()
