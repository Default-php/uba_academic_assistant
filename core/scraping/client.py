"""Cliente Moodle: Chrome headless con sesión de login y cookies para requests."""

import time

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from core.scraping.constants import LOGIN_URL, PASSWORD_FIELD_ID, USERNAME_FIELD_ID


class MoodleLoginError(Exception):
    """No se pudo iniciar sesión en el campus."""


class MoodleClient:
    """Maneja el navegador headless y la sesión contra el campus UBA."""

    def __init__(self, ci: str, password: str):
        self.ci = ci
        self.password = password
        self.driver = None

    def start(self) -> "MoodleClient":
        """Lanza Chrome headless y devuelve el cliente."""
        chrome_opts = Options()
        chrome_opts.add_argument("--headless=new")
        chrome_opts.add_argument("--disable-gpu")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        chrome_opts.add_argument("--window-size=1920,1080")
        # Espera solo DOMContentLoaded en vez de la carga completa: evita
        # colgarse por recursos lentos del campus.
        chrome_opts.page_load_strategy = "eager"

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_opts)
        self.driver.set_page_load_timeout(60)
        return self

    def _get_with_retry(self, url: str) -> None:
        """Navega a una URL reintentando una vez si el campus tarda demasiado.

        El campus es intermitentemente lento; un primer timeout no significa
        que esté caído. Se detiene la carga y se reintenta una vez.
        """
        for attempt in range(2):
            try:
                self.driver.get(url)
                return
            except (TimeoutException, WebDriverException):
                if attempt == 0:
                    # Detiene la carga colgada antes de reintentar.
                    self.driver.execute_script("window.stop()")
                    continue
                raise

    def login(self) -> "MoodleClient":
        """Navega al login, rellena credenciales y envía el formulario."""
        self._get_with_retry(LOGIN_URL)
        user_input = self.driver.find_element(By.ID, USERNAME_FIELD_ID)
        pass_input = self.driver.find_element(By.ID, PASSWORD_FIELD_ID)
        user_input.send_keys(self.ci)
        pass_input.send_keys(self.password)
        pass_input.send_keys(Keys.RETURN)

        # Espera a que el formulario desaparezca o la URL salga del login.
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: (
                    d.current_url != LOGIN_URL
                    or len(d.find_elements(By.ID, USERNAME_FIELD_ID)) == 0
                )
            )
        except TimeoutException as exc:
            raise MoodleLoginError("No se pudo iniciar sesión en el campus") from exc
        return self

    def go(self, url: str) -> None:
        """Navega a una URL y espera a que cargue."""
        self._get_with_retry(url)
        # Espera a que el DOM esté listo en vez de dormir a ciegas.
        try:
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script("return document.readyState")
                in (
                    "interactive",
                    "complete",
                )
            )
        except TimeoutException:
            pass
        time.sleep(1)

    def cookies_to_requests(self) -> requests.Session:
        """Devuelve una sesión de requests con las cookies del driver."""
        session = requests.Session()
        for c in self.driver.get_cookies():
            session.cookies.set(c["name"], c["value"])
        return session

    def quit(self) -> None:
        """Cierra el navegador."""
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def __enter__(self) -> "MoodleClient":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.quit()
