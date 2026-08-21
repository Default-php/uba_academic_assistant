"""Vista del endpoint de chat del asistente."""

import json
import logging

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from core.utils.openrouter_client import ChatUnavailableError, chat_with_model

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class AssistantAPIView(View):
    """
    Endpoint que recibe JSON { messages: [ { role, content }, ... ] }
    y responde { reply: '...' }. Usa chat_with_model para invocar a OpenRouter.
    """

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Autenticación requerida"}, status=401)

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

        messages = payload.get("messages")
        if not isinstance(messages, list) or not messages:
            return JsonResponse({"error": 'Debe enviar un array "messages" no vacío'}, status=400)

        try:
            result = chat_with_model(messages)
            return JsonResponse({"reply": result["content"]})
        except ChatUnavailableError:
            return JsonResponse(
                {"error": "El asistente no está configurado (falta OPENROUTER_API_KEY)"},
                status=503,
            )
        except Exception:
            logger.exception("Error en AssistantAPIView")
            return JsonResponse({"error": "Error interno del asistente"}, status=500)
