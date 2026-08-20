"""Cliente Moodle: Chrome headless con sesión de login y cookies para requests."""
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

from core.scraping.constants import LOGIN_URL, PASSWORD_FIELD_ID, USERNAME_FIELD_ID


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

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_opts)
        return self

    def login(self) -> "MoodleClient":
        """Navega al login, rellena credenciales y envía el formulario."""
        self.driver.get(LOGIN_URL)
        user_input = self.driver.find_element(By.ID, USERNAME_FIELD_ID)
        pass_input = self.driver.find_element(By.ID, PASSWORD_FIELD_ID)
        user_input.send_keys(self.ci)
        pass_input.send_keys(self.password)
        pass_input.send_keys(Keys.RETURN)
        time.sleep(3)
        return self

    def go(self, url: str) -> None:
        """Navega a una URL y espera a que cargue."""
        self.driver.get(url)
        time.sleep(2)

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
