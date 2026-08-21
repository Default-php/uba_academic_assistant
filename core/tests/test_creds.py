"""Tests de la resolución de credenciales UBA para los comandos CLI."""

from unittest.mock import patch

from django.core.management.base import CommandError
from django.test import SimpleTestCase

from core.utils.creds import resolve_creds


class ResolveCredsTests(SimpleTestCase):
    """resolve_creds combina --ci/--password con las vars de .env."""

    def test_usa_argumentos_si_se_pasan(self):
        ci, password = resolve_creds("111", "pass")
        self.assertEqual((ci, password), ("111", "pass"))

    @patch.dict("os.environ", {"UBA_USER_CI": "222", "UBA_USER_PASSWD": "envpass"})
    def test_cae_a_env_cuando_faltan_argumentos(self):
        ci, password = resolve_creds(None, None)
        self.assertEqual((ci, password), ("222", "envpass"))

    @patch.dict("os.environ", {"UBA_USER_CI": "222", "UBA_USER_PASSWD": "envpass"})
    def test_argumento_ci_gana_a_env(self):
        ci, password = resolve_creds("111", None)
        self.assertEqual((ci, password), ("111", "envpass"))

    @patch.dict("os.environ", {"UBA_USER_CI": "222", "UBA_USER_PASSWD": "envpass"})
    def test_argumento_password_gana_a_env(self):
        ci, password = resolve_creds(None, "argpass")
        self.assertEqual((ci, password), ("222", "argpass"))

    @patch.dict("os.environ", {"UBA_USER_CI": "222"})
    @patch("core.utils.creds.getpass", return_value="prompted")
    def test_pide_password_por_prompt_si_no_hay_env(self, mock_getpass):
        ci, password = resolve_creds(None, None)
        self.assertEqual((ci, password), ("222", "prompted"))
        mock_getpass.assert_called_once()

    @patch.dict("os.environ", {}, clear=True)
    def test_sin_ci_lanza_command_error(self):
        with self.assertRaises(CommandError):
            resolve_creds(None, None)
