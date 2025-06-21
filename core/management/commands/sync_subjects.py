import re
from time import sleep
from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from core.models import Subject
from dotenv import load_dotenv
import os

load_dotenv()
USERNAME = os.getenv("UBA_USERNAME")
PASSWORD = os.getenv("UBA_PASSWORD")

LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"
COURSES_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/my/courses.php"

ROMAN_NUMS = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12
}


def extraer_trimestre_y_nombre(texto):
    match = re.match(r"^([IVXL]+)\.\s*-\s*(.+)$", texto.strip())
    if match:
        romano = match.group(1).strip()
        nombre = match.group(2).strip()
        trimestre = ROMAN_NUMS.get(romano.upper(), None)
        return trimestre, nombre
    return None, texto


class Command(BaseCommand):
    help = "Sincroniza las materias del portal UBA a la base de datos"

    def handle(self, *args, **kwargs):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(LOGIN_URL)

        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)

        sleep(3)
        driver.get(COURSES_URL)
        sleep(3)

        cursos = driver.find_elements(By.CSS_SELECTOR, "a.coursename[href*='course/view.php?id=']")
        materias = []

        for curso in cursos:
            href = curso.get_attribute("href")
            nombre_span = curso.find_element(By.CLASS_NAME, "multiline")
            nombre_raw = nombre_span.text.strip()
            course_id = href.split("id=")[-1]
            trimestre, nombre_limpio = extraer_trimestre_y_nombre(nombre_raw)
            materias.append({
                "codigo": course_id,
                "nombre": nombre_limpio,
                "trimestre": trimestre or 0
            })

        driver.quit()

        for m in materias:
            existente = Subject.objects.filter(codigo=m["codigo"]).first()
            if not existente:
                Subject.objects.create(
                    codigo=m["codigo"],
                    nombre=m["nombre"],
                    trimestre=m["trimestre"]
                )
                self.stdout.write(self.style.SUCCESS(f"✔ Guardada: {m['nombre']} (ID {m['codigo']})"))
            else:
                self.stdout.write(f"⏩ Ya existe: {m['nombre']} (ID {m['codigo']})")
