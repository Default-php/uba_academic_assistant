"""Tests de la API REST (DRF)."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Evaluation, Subject
from core.views import SubjectViewSet

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

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.client.force_authenticate(user=self.user)

    def test_metodos_de_escritura_devuelven_405(self):
        url = reverse("user-detail", args=[self.user.pk])
        for method in ("patch", "put", "delete"):
            with self.subTest(method=method):
                response = getattr(self.client, method)(url, {"nombre_completo": "Ana B"})
                self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_me_no_expone_campos_sensibles(self):
        url = reverse("user-me")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for campo in ("is_staff", "is_superuser", "password"):
            self.assertNotIn(campo, response.data)


class UserOwnershipTests(APITestCase):
    """Un usuario no staff solo puede ver su propio perfil."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )
        self.user_b = User.objects.create_user(
            ci="222", nombre_completo="Beto", correo="beto@example.com"
        )

    def test_no_staff_no_puede_ver_otro_usuario(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("user-detail", args=[self.user_b.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubjectViewSetFilteringTests(APITestCase):
    """Cada usuario solo ve sus materias y las evaluaciones prefetched."""

    def setUp(self):
        self.user_a = User.objects.create_user(
            ci="111", nombre_completo="Ana", correo="ana@example.com"
        )
        self.user_b = User.objects.create_user(
            ci="222", nombre_completo="Beto", correo="beto@example.com"
        )
        self.subject_a = Subject.objects.create(codigo="101", nombre="Matemática", trimestre=1)
        self.subject_b = Subject.objects.create(codigo="102", nombre="Física", trimestre=1)
        Evaluation.objects.create(
            user=self.user_a, subject=self.subject_a, moodle_id="a1", titulo="Eval A"
        )
        Evaluation.objects.create(
            user=self.user_b, subject=self.subject_b, moodle_id="b1", titulo="Eval B"
        )

    def test_filtra_materias_y_evaluaciones_por_usuario(self):
        for user, codigo, moodle_id in (
            (self.user_a, "101", "a1"),
            (self.user_b, "102", "b1"),
        ):
            with self.subTest(user=user.ci):
                self.client.force_authenticate(user=user)
                url = reverse("subject-list")
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), 1)
                self.assertEqual(response.data[0]["codigo"], codigo)

                # El prefetch (to_attr="user_evals") solo trae las evaluaciones del usuario
                viewset = SubjectViewSet()
                viewset.request = type("FakeRequest", (), {"user": user})()
                subj = viewset.get_queryset().get()
                self.assertEqual([e.moodle_id for e in subj.user_evals], [moodle_id])


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


class AssistantChatAPITests(APITestCase):
    """Endpoint de chat del asistente (/api/chat/)."""

    def setUp(self):
        self.user = User.objects.create_user(
            ci="111",
            nombre_completo="Ana",
            correo="ana@example.com",
            password="secreta123",
        )
        self.url = reverse("api_chat")
        self.payload = {"messages": [{"role": "user", "content": "hola"}]}

    def test_ruta_resuelve_a_api_chat(self):
        self.assertEqual(reverse("api_chat"), "/api/chat/")

    def test_anonimo_devuelve_401(self):
        response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error"], "Autenticación requerida")

    def test_sin_api_key_devuelve_503(self):
        self.client.force_login(self.user)
        with override_settings(OPENROUTER_API_KEY=""):
            response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertIn("OPENROUTER_API_KEY", response.json()["error"])

    def test_con_api_key_devuelve_reply(self):
        self.client.force_login(self.user)
        with override_settings(OPENROUTER_API_KEY="clave-falsa"):
            with patch(
                "core.view.assistant.chat_with_model",
                return_value={"role": "assistant", "content": "hola"},
            ):
                response = self.client.post(self.url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["reply"], "hola")

    def test_json_invalido_devuelve_400(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data="no-json", content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error"], "JSON inválido")

    def test_messages_vacio_devuelve_400(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {"messages": []}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("messages", response.json()["error"])
