"""Tests del cliente OpenAI (import sin clave y error controlado)."""

import importlib

from django.test import SimpleTestCase, override_settings


class OpenAIClientImportTests(SimpleTestCase):
    """El módulo debe importarse aunque falte OPENAI_API_KEY."""

    @override_settings(OPENAI_API_KEY="")
    def test_importa_sin_api_key(self):
        module = importlib.import_module("core.utils.openai_client")
        self.assertTrue(hasattr(module, "chat_with_gpt"))
        self.assertTrue(hasattr(module, "ChatUnavailableError"))

    @override_settings(OPENAI_API_KEY="")
    def test_chat_with_gpt_sin_clave_lanza_chat_unavailable(self):
        module = importlib.import_module("core.utils.openai_client")
        with self.assertRaises(module.ChatUnavailableError):
            module.chat_with_gpt([{"role": "user", "content": "hola"}])
