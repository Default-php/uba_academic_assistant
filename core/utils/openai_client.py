import openai
from django.conf import settings

def chat_with_gpt(messages: list[dict], 
                  model: str = None, 
                  temperature: float = 0.7) -> dict:
    """
    Envía la lista de mensajes a la API de ChatGPT y devuelve la respuesta completa.
      - messages: lista de dicts con 'role' y 'content'
      - model: nombre del modelo (p. ej. 'gpt-4')
      - temperature: controla creatividad (0–1)
    """
    chosen_model = model or settings.OPENAI_DEFAULT_MODEL
    response = openai.ChatCompletion.create(
        model=chosen_model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message