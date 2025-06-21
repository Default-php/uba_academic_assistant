import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# Cargar .env para credenciales
load_dotenv()
USERNAME = os.getenv("UBA_USERNAME")
PASSWORD = os.getenv("UBA_PASSWORD")
LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"


def iniciar_sesion():
    """Inicia sesión y devuelve el driver con sesión activa."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(LOGIN_URL)

    time.sleep(1)
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "password").send_keys(PASSWORD + Keys.RETURN)
    time.sleep(2)
    return driver


def ir_a_url(driver, url):
    """Navega a una URL y espera que cargue."""
    driver.get(url)
    time.sleep(2)
