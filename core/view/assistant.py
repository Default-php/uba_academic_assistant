import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from core.utils.openai_client import chat_with_gpt

@method_decorator(csrf_exempt, name='dispatch')
class AssistantAPIView(View):
    """
    Endpoint que recibe { message: '...' } y responde { reply: '...' }.
    Usa el helper chat_with_gpt para invocar a OpenAI.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_msg = data.get('message', '').strip()
            if not user_msg:
                return JsonResponse({'error': 'No message provided'}, status=400)

            # Mensajes iniciales del sistema
            system_msg = {
                'role': 'system',
                'content': (
                    'Eres un asistente académico especializado en aclarar dudas '
                    'sobre evaluaciones de UBA. Responde con tono amable y claro.'
                )
            }
            # Mensaje del usuario
            user_entry = {'role': 'user', 'content': user_msg}

            # Invoca a ChatGPT-4.1
            response = chat_with_gpt([system_msg, user_entry])
            return JsonResponse({'reply': response['content']})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)