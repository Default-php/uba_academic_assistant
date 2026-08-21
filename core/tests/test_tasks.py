"""Tests del pipeline de sincronización (core.tasks.sync_for_user)."""

from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Evaluation, Subject
from core.tasks import sync_for_user

User = get_user_model()


class SyncForUserTests(TestCase):
    """Pruebas de sync_for_user con scraping mockeado."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )

    def _scrape_subjects(self, client):
        return [{"codigo": "101", "nombre": "Matemática", "trimestre": 1}]

    def _scrape_professors(self, client):
        return [{"codigo": "101", "profesor": "Oswald Carvajal"}]

    def _scrape_evaluations(self, client):
        return [
            {
                "subject_codigo": "101",
                "moodle_id": "m1",
                "titulo": "Parcial 1",
                "url": "http://example.com/eval",
                "numero": "1",
                "unidad": "1",
                "tipo": "Parcial",
                "seccion": "1",
                "profesor": "Oswald Carvajal",
                "porcentaje": "25",
                "fecha_inicio": None,
                "fecha_cierre": None,
                "contenido_html": "",
            }
        ]

    @patch("core.tasks.scrape_evaluations")
    @patch("core.tasks.scrape_professors")
    @patch("core.tasks.scrape_subjects")
    @patch("core.tasks.MoodleClient")
    def test_exito_crea_datos_y_marca_sincronizado(
        self, mock_client, mock_subjects, mock_professors, mock_evals
    ):
        mock_client.return_value.__enter__.return_value = MagicMock()
        mock_subjects.side_effect = self._scrape_subjects
        mock_professors.side_effect = self._scrape_professors
        mock_evals.side_effect = self._scrape_evaluations

        sync_for_user(self.user.pk, "111", "secreta")

        # Materia creada con su profesor
        subject = Subject.objects.get(codigo="101")
        self.assertEqual(subject.nombre, "Matemática")
        self.assertEqual(subject.profesor, "Oswald Carvajal")

        # Evaluación creada
        ev = Evaluation.objects.get(user=self.user)
        self.assertEqual(ev.moodle_id, "m1")
        self.assertEqual(ev.subject, subject)

        # Usuario marcado como sincronizado
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_synced)
        self.assertIsNotNone(self.user.last_synced)

    @patch("core.tasks.scrape_evaluations")
    @patch("core.tasks.scrape_professors")
    @patch("core.tasks.scrape_subjects")
    @patch("core.tasks.MoodleClient")
    def test_usuario_sincronizado_no_scrapea(
        self, mock_client, mock_subjects, mock_professors, mock_evals
    ):
        self.user.is_synced = True
        self.user.save(update_fields=["is_synced"])

        sync_for_user(self.user.pk, "111", "secreta")

        mock_subjects.assert_not_called()
        mock_professors.assert_not_called()
        mock_evals.assert_not_called()
        mock_client.assert_not_called()

    @patch("core.tasks.scrape_evaluations")
    @patch("core.tasks.scrape_professors")
    @patch("core.tasks.scrape_subjects")
    @patch("core.tasks.MoodleClient")
    def test_error_en_scrape_no_marca_sincronizado(
        self, mock_client, mock_subjects, mock_professors, mock_evals
    ):
        mock_client.return_value.__enter__.return_value = MagicMock()
        mock_subjects.side_effect = RuntimeError("campus caído")

        # No debe propagar la excepción
        sync_for_user(self.user.pk, "111", "secreta")

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_synced)

    @patch("core.tasks.scrape_evaluations")
    @patch("core.tasks.scrape_professors")
    @patch("core.tasks.scrape_subjects")
    @patch("core.tasks.MoodleClient")
    def test_usuario_desconocido_retorna_sin_error(
        self, mock_client, mock_subjects, mock_professors, mock_evals
    ):
        # pk inexistente: debe retornar sin lanzar ni scrapear
        sync_for_user(999999, "111", "secreta")
        mock_client.assert_not_called()
        mock_subjects.assert_not_called()
