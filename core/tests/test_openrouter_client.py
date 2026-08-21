"""Tests del cliente OpenRouter (import sin clave, errores y payload)."""

import importlib
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings

from core.utils.openrouter_client import ChatUnavailableError, chat_with_model


class OpenRouterClientImportTests(SimpleTestCase):
    """El módulo debe importarse aunque falte OPENROUTER_API_KEY."""

    @override_settings(OPENROUTER_API_KEY="")
    def test_importa_sin_api_key(self):
        module = importlib.import_module("core.utils.openrouter_client")
        self.assertTrue(hasattr(module, "chat_with_model"))
        self.assertTrue(hasattr(module, "ChatUnavailableError"))

    @override_settings(OPENROUTER_API_KEY="")
    def test_chat_with_model_sin_clave_lanza_chat_unavailable(self):
        with self.assertRaises(ChatUnavailableError):
            chat_with_model([{"role": "user", "content": "hola"}])


class OpenRouterClientChatTests(SimpleTestCase):
    """chat_with_model construye la petición y parsea la respuesta."""

    @override_settings(
        OPENROUTER_API_KEY="clave-falsa",
        OPENROUTER_DEFAULT_MODEL="meta-llama/llama-3.3-70b-instruct:free",
        OPENROUTER_MAX_TOKENS=1200,
    )
    @patch("core.utils.openrouter_client.requests.post")
    def test_envia_payload_y_parsea_respuesta(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": "hola"}}]
        }
        mock_post.return_value = mock_response

        messages = [{"role": "user", "content": "hola"}]
        result = chat_with_model(messages)

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer clave-falsa")
        self.assertEqual(kwargs["headers"]["Content-Type"], "application/json")
        self.assertEqual(kwargs["headers"]["HTTP-Referer"], "https://uba-assistant.local")
        self.assertEqual(kwargs["headers"]["X-Title"], "UBA Assistant")
        self.assertEqual(kwargs["json"]["model"], "meta-llama/llama-3.3-70b-instruct:free")
        self.assertEqual(kwargs["json"]["messages"], messages)
        self.assertEqual(kwargs["json"]["max_tokens"], 1200)
        self.assertEqual(kwargs["timeout"], 60)

        self.assertEqual(result, {"role": "assistant", "content": "hola"})

    @override_settings(OPENROUTER_API_KEY="clave-falsa")
    @patch("core.utils.openrouter_client.requests.post")
    def test_content_vacio_devuelve_cadena_vacia(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{"message": {"role": "assistant", "content": None}}]
        }
        mock_post.return_value = mock_response

        result = chat_with_model([{"role": "user", "content": "hola"}])
        self.assertEqual(result, {"role": "assistant", "content": ""})

    @override_settings(OPENROUTER_API_KEY="clave-falsa")
    @patch("core.utils.openrouter_client.requests.post")
    def test_error_http_se_propaga(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = RuntimeError("HTTP 429")
        mock_post.return_value = mock_response

        with self.assertRaises(RuntimeError):
            chat_with_model([{"role": "user", "content": "hola"}])

    @override_settings(OPENROUTER_API_KEY="clave-falsa")
    @patch("core.utils.openrouter_client.requests.post")
    def test_respuesta_inesperada_lanza_chat_unavailable(self, mock_post):
        mock_response = Mock()
        mock_response.json.return_value = {"foo": "bar"}
        mock_post.return_value = mock_response

        with self.assertRaises(ChatUnavailableError) as ctx:
            chat_with_model([{"role": "user", "content": "hola"}])
        self.assertEqual(str(ctx.exception), "Respuesta inesperada de OpenRouter")
