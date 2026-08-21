"""Tests del scraping de profesores (core.scraping.professors)."""

from django.test import TestCase

from core.models import Subject
from core.scraping.professors import scrape_professors


class _FakeElement:
    """Elemento de Selenium con texto visible o solo accesible por textContent."""

    def __init__(self, text="", text_content=None):
        self._text = text
        self._text_content = text if text_content is None else text_content

    @property
    def text(self):
        return self._text

    def get_attribute(self, name):
        if name == "textContent":
            return self._text_content
        return None


class _FakeDriver:
    def __init__(self, element, raises=False):
        self._element = element
        self._raises = raises

    def find_element(self, by, selector):
        if self._raises:
            raise Exception("elemento no encontrado")
        return self._element


class _FakeClient:
    def __init__(self, driver):
        self.driver = driver

    def go(self, url):
        pass


class ScrapeProfessorsTests(TestCase):
    def setUp(self):
        self.s1 = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)
        self.s2 = Subject.objects.create(codigo="102", nombre="Física", trimestre=1)

    def test_usa_textcontent_cuando_el_elemento_esta_oculto(self):
        """El tema actual oculta el bloque messageteacher: .text es vacío y
        el nombre solo está disponible vía textContent."""
        driver = _FakeDriver(_FakeElement(text="", text_content="Oswald Carvajal"))
        client = _FakeClient(driver)

        profs = scrape_professors(client)

        self.assertEqual(len(profs), 2)
        self.assertEqual(profs[0]["codigo"], "101")
        self.assertEqual(profs[0]["profesor"], "Oswald Carvajal")

    def test_usa_textcontent_cuando_text_es_solo_espacios(self):
        """Un .text de solo espacios es truthy pero no tiene nombre: se debe
        normalizar antes de decidir y usar textContent como respaldo."""
        driver = _FakeDriver(_FakeElement(text="   ", text_content="MARIA PEREZ"))
        client = _FakeClient(driver)

        profs = scrape_professors(client)

        self.assertEqual(profs[0]["profesor"], "MARIA PEREZ")

    def test_usa_text_visible_cuando_existe(self):
        driver = _FakeDriver(_FakeElement(text="Ana Miranda"))
        client = _FakeClient(driver)

        profs = scrape_professors(client)

        self.assertEqual(profs[0]["profesor"], "Ana Miranda")

    def test_sin_elemento_devuelve_none(self):
        driver = _FakeDriver(element=None, raises=True)
        client = _FakeClient(driver)

        profs = scrape_professors(client)

        self.assertEqual(profs[0]["profesor"], None)
