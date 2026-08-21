"""Tests de modelos y del manager de usuario."""

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from core.models import AgentInteraction, Evaluation, Subject

User = get_user_model()


class CustomUserManagerTests(TestCase):
    """Pruebas del manager de usuario."""

    def test_create_user_requiere_ci(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(ci="", nombre_completo="Ana", correo="ana@example.com")

    def test_create_user_requiere_correo(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(ci="12345", nombre_completo="Ana", correo="")

    def test_create_user_con_password(self):
        user = User.objects.create_user(
            ci="12345",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.assertTrue(user.check_password("secreta123"))
        self.assertEqual(user.correo, "ana@example.com")


class EvaluationUniqueTogetherTests(TestCase):
    """La combinación (user, moodle_id) debe ser única."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )
        self.subject = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)

    def test_duplicado_lanza_integrity_error(self):
        Evaluation.objects.create(
            user=self.user,
            subject=self.subject,
            moodle_id="m1",
            titulo="Parcial 1",
        )
        with self.assertRaises(IntegrityError):
            Evaluation.objects.create(
                user=self.user,
                subject=self.subject,
                moodle_id="m1",
                titulo="Parcial 1 duplicado",
            )


class SubjectStrTests(TestCase):
    """Representación en texto de Subject."""

    def test_str(self):
        subject = Subject(codigo="101", nombre="Matemática")
        self.assertEqual(str(subject), "101 - Matemática")


class AgentInteractionTests(TestCase):
    """Modelo AgentInteraction (historial del asistente)."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )

    def test_create_y_str(self):
        interaction = AgentInteraction.objects.create(
            usuario=self.user,
            pregunta="¿Cuándo es el parcial?",
            respuesta_generada="El 15 de agosto.",
            intencion_detectada="consulta_fecha",
            confianza="0.85",
        )
        self.assertEqual(AgentInteraction.objects.count(), 1)
        self.assertEqual(str(interaction), "Ana → consulta_fecha")

    def test_str_sin_intencion(self):
        interaction = AgentInteraction.objects.create(
            usuario=self.user,
            pregunta="Hola",
            respuesta_generada="Hola, ¿en qué te ayudo?",
        )
        self.assertEqual(str(interaction), "Ana → Pregunta")
