"""Scraping de profesores del campus UBA."""
from selenium.webdriver.common.by import By

from core.models import Subject
from core.scraping.constants import BASE_URL, TEACHER_LINK_SELECTOR


def scrape_professors(client) -> list[dict]:
    """
    Hace login y para cada materia en la BD extrae el nombre del profesor.
    Devuelve lista de dicts: {"codigo", "profesor"}.
    """
    client.login()

    professors = []
    for subj in Subject.objects.all():
        course_url = f"{BASE_URL}course/view.php?id={subj.codigo}"
        client.go(course_url)
        try:
            span = client.driver.find_element(By.CSS_SELECTOR, TEACHER_LINK_SELECTOR)
            nombre = span.text.strip()
        except Exception:
            nombre = None
        professors.append({
            "codigo": subj.codigo,
            "profesor": nombre,
        })

    return professors
