# core/views/assistant.py

import json
import logging
import traceback

from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.utils.openai_client import chat_with_gpt

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class AssistantAPIView(View):
    """
    Endpoint que recibe JSON { messages: [ { role, content }, … ] }
    y responde { reply: '…' }. Usa chat_with_gpt para invocar a OpenAI.
    """
    def post(self, request, *args, **kwargs):
        # 1) Parseo del body
        try:
            payload = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)

        # 2) Validación de messages
        messages = payload.get('messages')
        if not isinstance(messages, list) or not messages:
            return JsonResponse(
                {'error': 'Debe enviar un array "messages" no vacío'},
                status=400
            )

        # 3) Llamada al helper de OpenAI
        try:
            result = chat_with_gpt(messages)
            return JsonResponse({'reply': result['content']})

        except Exception as exc:
            # Log completo en servidor
            logger.exception("Error en AssistantAPIView")

            # Devuelve siempre el mensaje de error real + traza
            return JsonResponse({
                'error': str(exc),
                'trace': traceback.format_exc()
            }, status=500)
