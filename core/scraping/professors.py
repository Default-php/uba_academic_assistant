"""Scraping de profesores del campus UBA."""

from selenium.webdriver.common.by import By

from core.models import Subject
from core.scraping.constants import BASE_URL, TEACHER_LINK_SELECTOR


def scrape_professors(client) -> list[dict]:
    """
    Asume que el cliente ya está autenticado (login hecho por el llamador).
    Para cada materia en la BD extrae el nombre del profesor.
    Devuelve lista de dicts: {"codigo", "profesor"}.
    """
    professors = []
    for subj in Subject.objects.all():
        course_url = f"{BASE_URL}course/view.php?id={subj.codigo}"
        client.go(course_url)
        try:
            span = client.driver.find_element(By.CSS_SELECTOR, TEACHER_LINK_SELECTOR)
            # El bloque "messageteacher" puede estar oculto en el tema actual:
            # Selenium devuelve .text vacío para elementos no visibles, así que
            # se usa textContent como respaldo.
            texto = (span.text or "").strip() or (span.get_attribute("textContent") or "").strip()
            nombre = texto or None
        except Exception:
            nombre = None
        professors.append(
            {
                "codigo": subj.codigo,
                "profesor": nombre,
            }
        )

    return professors
