"""Cliente OpenAI para el asistente de chat.

El módulo no lanza errores al importarse aunque falte OPENAI_API_KEY:
la clave se lee de forma perezosa dentro de chat_with_gpt para que la
aplicación pueda arrancar sin ella.
"""

from django.conf import settings

DEFAULT_MODEL = getattr(settings, "OPENAI_DEFAULT_MODEL", "gpt-3.5-turbo")
DEFAULT_MAX_TOKENS = getattr(settings, "OPENAI_MAX_TOKENS", None)


class ChatUnavailableError(Exception):
    """El asistente no está configurado (falta OPENAI_API_KEY)."""


def chat_with_gpt(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = None,
) -> dict:
    """
    Envía mensajes a OpenAI chat.completions.create y devuelve {'role', 'content'}.

    - messages: [{'role': 'system'|'user'|'assistant', 'content': str}, ...]
    - model: opcional, sino usa DEFAULT_MODEL
    - temperature: creatividad (0-1)
    - max_tokens: opcional, sino usa DEFAULT_MAX_TOKENS
    """
    api_key = getattr(settings, "OPENAI_API_KEY", "")
    if not api_key:
        raise ChatUnavailableError("OPENAI_API_KEY no está configurado")

    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    model_name = model or DEFAULT_MODEL
    tok_limit = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
    }
    if tok_limit is not None:
        payload["max_tokens"] = tok_limit

    response = client.chat.completions.create(**payload)
    msg = response.choices[0].message

    return {
        "role": msg.role,
        "content": msg.content,
    }
