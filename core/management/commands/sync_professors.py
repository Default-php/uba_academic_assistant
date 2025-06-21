from django.core.management.base import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from core.models import Subject
from dotenv import load_dotenv
import os
from time import sleep

load_dotenv()
USERNAME = os.getenv("UBA_USERNAME")
PASSWORD = os.getenv("UBA_PASSWORD")
LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"

class Command(BaseCommand):
    help = "Sincroniza los nombres de los profesores para cada materia"

    def handle(self, *args, **options):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get(LOGIN_URL)

        # Iniciar sesión
        username_input = driver.find_element(By.ID, "username")
        password_input = driver.find_element(By.ID, "password")
        username_input.send_keys(USERNAME)
        password_input.send_keys(PASSWORD)
        password_input.send_keys("\n")

        sleep(3)

        subjects = Subject.objects.all()

        for subject in subjects:
            course_url = f"https://pregrado.campusvirtualuba.net.ve/trimestre/course/view.php?id={subject.codigo}"
            driver.get(course_url)
            sleep(2)

            try:
                enlace_profesor = driver.find_element(By.CSS_SELECTOR, "a.messageteacher_link span")
                nombre_profesor = enlace_profesor.text.strip()

                subject.profesor = nombre_profesor
                subject.save()

                self.stdout.write(self.style.SUCCESS(f"✔ Profesor actualizado: {subject.nombre} → {nombre_profesor}"))

            except Exception as e:
                self.stdout.write(self.style.WARNING(f"⚠️ No se encontró profesor para {subject.nombre} (ID {subject.codigo})"))

        driver.quit()
        self.stdout.write(self.style.SUCCESS("Sincronización de profesores completada."))
