"""Tests del cliente Moodle (core.scraping.client) con webdriver mockeado."""

from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from selenium.common.exceptions import TimeoutException

from core.scraping.client import MoodleClient, MoodleLoginError
from core.scraping.constants import PASSWORD_FIELD_ID, USERNAME_FIELD_ID


def _make_client():
    """Devuelve un MoodleClient con driver mockeado ya iniciado."""
    client = MoodleClient("111", "secreta")
    client.driver = MagicMock()
    return client


class MoodleClientStartTests(SimpleTestCase):
    """Opciones de Chrome y timeouts al arrancar."""

    @patch("core.scraping.client.ChromeDriverManager")
    @patch("core.scraping.client.webdriver.Chrome")
    def test_opciones_y_timeout(self, mock_chrome, mock_manager):
        mock_manager.return_value.install.return_value = "/fake/chromedriver"
        client = MoodleClient("111", "secreta")
        client.start()

        options = mock_chrome.call_args.kwargs["options"]
        self.assertEqual(options.page_load_strategy, "eager")
        driver = mock_chrome.return_value
        driver.set_page_load_timeout.assert_called_once_with(60)


class MoodleClientLoginTests(SimpleTestCase):
    """Login: rellena credenciales y espera el resultado."""

    def test_exito(self):
        client = _make_client()
        driver = client.driver
        driver.current_url = "https://campus/dashboard"
        driver.find_element.return_value = MagicMock()

        result = client.login()

        self.assertIs(result, client)
        driver.find_element.assert_any_call("id", USERNAME_FIELD_ID)
        driver.find_element.assert_any_call("id", PASSWORD_FIELD_ID)
        # El wait se resuelve sin lanzar excepción.

    @patch("core.scraping.client.WebDriverWait")
    def test_fallo_lanza_moodle_login_error(self, mock_wait):
        client = _make_client()
        mock_wait.return_value.until.side_effect = TimeoutException("timeout")

        with self.assertRaises(MoodleLoginError):
            client.login()


class MoodleClientGoTests(SimpleTestCase):
    """go() reintenta la navegación ante timeouts."""

    def test_reintenta_una_vez_y_exito(self):
        client = _make_client()
        driver = client.driver
        driver.get.side_effect = [TimeoutException("timeout"), None]
        driver.execute_script.return_value = "complete"

        client.go("https://campus/course")

        self.assertEqual(driver.get.call_count, 2)
        driver.execute_script.assert_any_call("window.stop()")

    def test_agota_reintentos_y_propaga(self):
        client = _make_client()
        driver = client.driver
        driver.get.side_effect = TimeoutException("timeout")

        with self.assertRaises(TimeoutException):
            client.go("https://campus/course")

        self.assertEqual(driver.get.call_count, 2)
        driver.execute_script.assert_any_call("window.stop()")


class MoodleClientQuitTests(SimpleTestCase):
    """quit() cierra el driver incluso tras errores de login."""

    @patch("core.scraping.client.WebDriverWait")
    def test_quit_llamado_en_contexto_con_error(self, mock_wait):
        mock_wait.return_value.until.side_effect = TimeoutException("timeout")
        client = _make_client()
        driver = client.driver

        # Evita lanzar Chrome real: el contexto usa el driver mockeado.
        with patch.object(client, "start", return_value=client):
            with self.assertRaises(MoodleLoginError):
                with client:
                    client.login()

        driver.quit.assert_called_once()
