"""Tests de los parsers de texto del campus (evaluaciones y materias)."""

from datetime import datetime

from django.test import SimpleTestCase

from core.scraping.parsers import extraer_trimestre_y_nombre, parse_evaluation_text


class ParseEvaluationTextTests(SimpleTestCase):
    """Pruebas de parse_evaluation_text con los ejemplos del módulo original."""

    def test_ejemplo_con_pipes(self):
        texto = (
            "Actividad Sumativa N° 1 │ Unidad 1 │ Informe de Investigación │ "
            "Sección 1 │ Prof. Oswald Carvajal │ 25%│ Fecha de Inicio: "
            "26/05/2025 │ Hora: 00:01 a.m. │ Fecha de Cierre: 30/05/2025 │ "
            "Hora: 23:59 p.m. │ Hora Venezuela │"
        )
        resultado = parse_evaluation_text(texto)
        self.assertEqual(resultado["numero"], "1")
        self.assertEqual(resultado["unidad"], "1")
        self.assertEqual(resultado["seccion"], "1")
        self.assertEqual(resultado["profesor"], "Oswald Carvajal")
        self.assertEqual(resultado["porcentaje"], 25)
        self.assertEqual(resultado["fecha_inicio"], datetime(2025, 5, 26))
        self.assertEqual(resultado["fecha_cierre"], datetime(2025, 5, 30))

    def test_ejemplo_con_pipes_ascii(self):
        texto = (
            "Actividad sumativa 3: Plan de acción | Sección 1 | "
            "Tutora: Adriana Miranda | 25% | Desde el 23/06/2025 a las 00:01 am "
            "hasta el 27/06/2025 a las 23:59 pm (Hora Venezuela)"
        )
        resultado = parse_evaluation_text(texto)
        self.assertEqual(resultado["seccion"], "1")
        self.assertEqual(resultado["profesor"], "Adriana Miranda")
        self.assertEqual(resultado["porcentaje"], 25)
        self.assertEqual(resultado["fecha_inicio"], datetime(2025, 6, 23))
        self.assertEqual(resultado["fecha_cierre"], datetime(2025, 6, 27))

    def test_sin_fechas_devuelve_none(self):
        texto = (
            "Actividad Sumativa N° 1 | Unidad 1 | Informe | Sección 1 | Prof. Oswald Carvajal | 25%"
        )
        resultado = parse_evaluation_text(texto)
        self.assertIsNone(resultado["fecha_inicio"])
        self.assertIsNone(resultado["fecha_cierre"])

    def test_una_sola_fecha_devuelve_none(self):
        texto = "Actividad N° 1 | Unidad 1 | Sección 1 | Prof. X | 25% | Fecha: 26/05/2025"
        resultado = parse_evaluation_text(texto)
        self.assertIsNone(resultado["fecha_inicio"])
        self.assertIsNone(resultado["fecha_cierre"])

    def test_unidad_sin_seccion(self):
        texto = "Actividad N° 2 | Unidad 3 | Examen | Prof. Juan Perez | 30%"
        resultado = parse_evaluation_text(texto)
        self.assertEqual(resultado["unidad"], "3")
        self.assertIsNone(resultado["seccion"])

    def test_sin_porcentaje(self):
        texto = "Actividad N° 1 | Unidad 1 | Informe | Sección 1 | Prof. Oswald Carvajal"
        resultado = parse_evaluation_text(texto)
        self.assertIsNone(resultado["porcentaje"])


class ExtraerTrimestreYNombreTests(SimpleTestCase):
    """Pruebas de extraer_trimestre_y_nombre."""

    def test_trimestre_romano(self):
        trimestre, nombre = extraer_trimestre_y_nombre("II.- - Nombre de Materia")
        self.assertEqual(trimestre, 2)
        self.assertEqual(nombre, "- Nombre de Materia")

    def test_sin_formato_romano(self):
        trimestre, nombre = extraer_trimestre_y_nombre("texto sin romano")
        self.assertEqual(trimestre, 0)
        self.assertEqual(nombre, "texto sin romano")
