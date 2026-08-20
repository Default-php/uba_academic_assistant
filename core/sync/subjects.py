import re
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL   = "https://pregrado.campusvirtualuba.net.ve/trimestre/login/index.php"
COURSES_URL = "https://pregrado.campusvirtualuba.net.ve/trimestre/my/courses.php"

ROMAN_NUMS = {
    'I': 1,   'II': 2,  'III': 3, 'IV': 4,
    'V': 5,   'VI': 6,  'VII': 7, 'VIII': 8,
    'IX': 9,  'X': 10,  'XI': 11, 'XII': 12
}

def extraer_trimestre_y_nombre(texto: str):
    """
    Dado un texto tipo "II.- - Nombre de Materia", devuelve
    (trimestre_numérico, nombre_limpio).    
    """
    match = re.match(r"^([IVXL]+)\.\s*-\s*(.+)$", texto.strip())
    if match:
        romano = match.group(1).strip()
        nombre = match.group(2).strip()
        return ROMAN_NUMS.get(romano.upper(), 0), nombre
    return 0, texto

def scrape_subjects(username: str, password: str) -> list[dict]:
    """
    Con Selenium hace login en UBA, extrae lista de materias y retorna:
      [
        {"codigo": "1234", "nombre": "Materia X", "trimestre": 2},
        ...
      ]
    """
    # Configura Chrome en modo headless
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

        # 2) Ir al listado de cursos
        driver.get(COURSES_URL)
        sleep(3)

        # 3) Extraer enlaces de materia
        links = driver.find_elements(
            By.CSS_SELECTOR,
            "a.coursename[href*='course/view.php?id=']"
        )

        materias = []
        for link in links:
            href = link.get_attribute("href")
            raw = link.find_element(By.CLASS_NAME, "multiline").text.strip()
            code = href.split("id=")[-1]
            trimestre, nombre = extraer_trimestre_y_nombre(raw)
            materias.append({
                "codigo":     code,
                "nombre":     nombre,
                "trimestre":  trimestre
            })

        return materias

    finally:
        driver.quit()