import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"

def scrape_professors(username: str, password: str) -> list[dict]:
    """
    Hace login en UBA y para cada materia en la BD extrae el nombre
    del profesor. Retorna:
      [
        {"codigo": "1234", "profesor": "Nombre Profesor"},
        ...
      ]
    """
    # Configura Chrome headless
    chrome_opts = Options()
    chrome_opts.add_argument("--headless")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_opts
    )

    try:
        # 1) Login
        driver.get(LOGIN_URL)
        u_in = driver.find_element(By.ID, "username")
        p_in = driver.find_element(By.ID, "password")
        u_in.send_keys(username)
        p_in.send_keys(password)
        p_in.send_keys(Keys.RETURN)
        sleep(3)

        # 2) Para cada materia en la BD (solo códigos)
        from core.models import Subject  # import tardío para evitar ciclos
        professors = []
        for subj in Subject.objects.all():
            course_url = (
                f"https://pregrado.campusvirtualuba.net.ve/"
                f"trimestre/course/view.php?id={subj.codigo}"
            )
            driver.get(course_url)
            sleep(2)
            try:
                span = driver.find_element(
                    By.CSS_SELECTOR,
                    "a.messageteacher_link span"
                )
                nombre = span.text.strip()
            except Exception:
                nombre = None
            professors.append({
                "codigo":    subj.codigo,
                "profesor":  nombre
            })

        return professors

    finally:
        driver.quit()