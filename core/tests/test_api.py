"""Tests de la API REST (DRF)."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Evaluation, Subject

User = get_user_model()


class RegisterAPITests(APITestCase):
    """Registro de usuarios."""

    def test_registro_exitoso(self):
        url = reverse("user-register")
        data = {
            "ci": "12345",
            "nombre_completo": "Ana",
            "correo": "ana@example.com",
            "password": "secreta123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(ci="12345").exists())

    def test_registro_ci_duplicado(self):
        User.objects.create_user(ci="12345", nombre_completo="Ana", correo="ana@example.com")
        url = reverse("user-register")
        data = {
            "ci": "12345",
            "nombre_completo": "Otra",
            "correo": "otra@example.com",
            "password": "secreta123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SyncAPITests(APITestCase):
    """Endpoint de sincronización en segundo plano."""

    def test_sync_anonimo_no_permitido(self):
        url = reverse("user-sync")
        response = self.client.post(url, {"ci": "111", "password": "x"})
        self.assertIn(
            response.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
        )

    def test_sync_autenticado_encola_tarea(self):
        user = User.objects.create_user(
            ci="111",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-sync")
        with patch("core.views.async_task") as mock_async:
            response = self.client.post(url, {"ci": "111", "password": "x"})
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_async.assert_called_once()
        args = mock_async.call_args[0]
        self.assertEqual(args[0], "core.tasks.sync_for_user")
        self.assertEqual(args[1], user.pk)


class LogoutAPITests(APITestCase):
    """Cierre de sesión con refresh token."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.client.force_authenticate(user=self.user)

    def test_logout_sin_refresh_devuelve_400(self):
        url = reverse("token_logout")
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_refresh_invalido_devuelve_400(self):
        url = reverse("token_logout")
        response = self.client.post(url, {"refresh": "token-invalido"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)


class UserViewSetReadOnlyTests(APITestCase):
    """El viewset de usuarios es de solo lectura."""

    def test_patch_usuario_devuelve_405(self):
        user = User.objects.create_user(
            ci="111",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.client.force_authenticate(user=user)
        url = reverse("user-detail", args=[user.pk])
        response = self.client.patch(url, {"nombre_completo": "Ana B"})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class EvaluationViewSetTests(APITestCase):
    """Cada usuario solo ve sus propias evaluaciones."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )
        self.user_b = User.objects.create_user(
            ci="222", nombre_completo="Beto", correo="beto@example.com"
        )
        self.subject = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)
        Evaluation.objects.create(
            user=self.user_a, subject=self.subject, moodle_id="a1", titulo="Eval A"
        )
        Evaluation.objects.create(
            user=self.user_b, subject=self.subject, moodle_id="b1", titulo="Eval B"
        )

    def test_solo_ve_sus_evaluaciones(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("evaluation-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["moodle_id"], "a1")
