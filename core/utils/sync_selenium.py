import os
from time import sleep
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Cargar credenciales desde .env
load_dotenv()
USERNAME = os.getenv("UBA_USERNAME")
PASSWORD = os.getenv("UBA_PASSWORD")

LOGIN_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"
COURSES_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/my/courses.php"


def iniciar_sesion_y_extraer_materias():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar sin abrir ventana
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(LOGIN_URL)

    # Completar formulario de login
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    password_input.send_keys(Keys.RETURN)

    sleep(3)  # Esperar a que cargue el panel de usuario

    driver.get(COURSES_URL)
    sleep(3)  # Esperar carga dinámica de cursos

    materias = []
    cursos = driver.find_elements(By.CSS_SELECTOR, "a.coursename[href*='course/view.php?id=']")

    for curso in cursos:
        href = curso.get_attribute("href")
        nombre_span = curso.find_element(By.CLASS_NAME, "multiline")
        nombre = nombre_span.text.strip()
        course_id = href.split("id=")[-1]
        materias.append({"id": course_id, "nombre": nombre})

    driver.quit()

    return materias


if __name__ == "__main__":
    materias = iniciar_sesion_y_extraer_materias()
    if materias:
        print("Materias encontradas:")
        for m in materias:
            print(f"- {m['id']}: {m['nombre']}")
    else:
        print("No se encontraron materias.")
