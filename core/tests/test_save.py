"""Tests de la persistencia de datos scrapeados (core.scraping.save)."""

from datetime import date, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Evaluation, Subject
from core.scraping.save import save_evaluations, save_professors, save_subjects

User = get_user_model()


class SaveSubjectsTests(TestCase):
    """save_subjects crea y actualiza materias por codigo."""

    def test_crea_materias(self):
        save_subjects(
            [
                {"codigo": "101", "nombre": "Matemática", "trimestre": 1},
                {"codigo": "102", "nombre": "Física", "trimestre": 2},
            ]
        )
        self.assertEqual(Subject.objects.count(), 2)
        self.assertEqual(Subject.objects.get(codigo="101").nombre, "Matemática")

    def test_actualiza_materia_existente(self):
        Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)
        save_subjects(
            [
                {"codigo": "101", "nombre": "Matemática Avanzada", "trimestre": 1},
            ]
        )
        self.assertEqual(Subject.objects.count(), 1)
        self.assertEqual(Subject.objects.get(codigo="101").nombre, "Matemática Avanzada")

    def test_nombre_colisionante_no_aborta_y_registra_warning(self):
        Subject.objects.create(codigo="1", nombre="X", trimestre=1)
        Subject.objects.create(codigo="2", nombre="Y", trimestre=1)
        with self.assertLogs("core.scraping.save", level="WARNING") as logs:
            save_subjects([{"codigo": "1", "nombre": "Y", "trimestre": 1}])
        # La materia A conserva su nombre y el resto de la sincronización sigue
        self.assertEqual(Subject.objects.get(codigo="1").nombre, "X")
        self.assertTrue(any("codigo 1" in msg for msg in logs.output))


class SaveProfessorsTests(TestCase):
    """save_professors actualiza el profesor de la materia por codigo."""

    def setUp(self):
        self.subject = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)

    def test_actualiza_profesor(self):
        save_professors([{"codigo": "101", "profesor": "Oswald Carvajal"}])
        self.subject.refresh_from_db()
        self.assertEqual(self.subject.profesor, "Oswald Carvajal")

    def test_materia_desconocida_no_falla(self):
        # No debe lanzar excepción si el codigo no existe
        save_professors([{"codigo": "999", "profesor": "Alguien"}])
        self.assertEqual(Subject.objects.count(), 1)


class SaveEvaluationsTests(TestCase):
    """save_evaluations borra las previas y crea las nuevas."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )
        self.subject = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)

    def _entry(self, moodle_id="m1", **overrides):
        entry = {
            "subject_codigo": "101",
            "moodle_id": moodle_id,
            "titulo": "Parcial 1",
            "url": "http://example.com/eval",
            "numero": "1",
            "unidad": "1",
            "tipo": "Parcial",
            "seccion": "1",
            "profesor": "Oswald Carvajal",
            "porcentaje": "25",
            "fecha_inicio": date(2025, 5, 26),
            "fecha_cierre": date(2025, 5, 30),
            "contenido_html": "<p>contenido</p>",
        }
        entry.update(overrides)
        return entry

    def test_borra_previas_y_crea_nuevas(self):
        # Evaluación previa que debe eliminarse
        Evaluation.objects.create(
            user=self.user,
            subject=self.subject,
            moodle_id="vieja",
            titulo="Vieja",
        )
        save_evaluations(self.user, [self._entry()])
        self.assertEqual(Evaluation.objects.filter(user=self.user).count(), 1)
        ev = Evaluation.objects.get(user=self.user)
        self.assertEqual(ev.moodle_id, "m1")
        self.assertEqual(ev.titulo, "Parcial 1")
        self.assertEqual(ev.subject, self.subject)

    def test_fechas_se_guardan_como_date(self):
        save_evaluations(self.user, [self._entry()])
        ev = Evaluation.objects.get(user=self.user)
        self.assertEqual(ev.fecha_inicio, date(2025, 5, 26))
        self.assertEqual(ev.fecha_cierre, date(2025, 5, 30))

    def test_fechas_datetime_se_convierten_a_date(self):
        # El parser puede devolver datetime; el campo es DateField
        save_evaluations(
            self.user,
            [
                self._entry(
                    fecha_inicio=datetime(2025, 5, 26, 0, 0),
                    fecha_cierre=datetime(2025, 5, 30, 23, 59),
                )
            ],
        )
        ev = Evaluation.objects.get(user=self.user)
        self.assertEqual(ev.fecha_inicio, date(2025, 5, 26))
        self.assertEqual(ev.fecha_cierre, date(2025, 5, 30))

    def test_materia_desconocida_se_omite(self):
        save_evaluations(self.user, [self._entry(subject_codigo="999")])
        self.assertEqual(Evaluation.objects.filter(user=self.user).count(), 0)
