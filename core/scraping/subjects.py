"""Scraping de materias del campus UBA."""

from selenium.webdriver.common.by import By

from core.scraping.constants import COURSE_LINK_SELECTOR, COURSES_URL
from core.scraping.parsers import extraer_trimestre_y_nombre


def scrape_subjects(client) -> list[dict]:
    """
    Asume que el cliente ya está autenticado (login hecho por el llamador).
    Extrae la lista de materias del campus.
    Devuelve lista de dicts: {"codigo", "nombre", "trimestre"}.
    """
    client.go(COURSES_URL)

    links = client.driver.find_elements(By.CSS_SELECTOR, COURSE_LINK_SELECTOR)

    materias = []
    for link in links:
        href = link.get_attribute("href")
        raw = link.find_element(By.CLASS_NAME, "multiline").text.strip()
        code = href.split("id=")[-1]
        trimestre, nombre = extraer_trimestre_y_nombre(raw)
        materias.append(
            {
                "codigo": code,
                "nombre": nombre,
                "trimestre": trimestre,
            }
        )

    return materias
