"""Cliente OpenRouter para el asistente de chat.

OpenRouter es una pasarela compatible con la API de OpenAI. El módulo no
lanza errores al importarse aunque falte OPENROUTER_API_KEY: la clave se lee
de forma perezosa dentro de chat_with_model para que la aplicación pueda
arrancar sin ella.
"""

import requests
from django.conf import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODEL = "meta-llama/llama-3.3-70b-instruct:free"


class ChatUnavailableError(Exception):
    """El asistente no está configurado (falta OPENROUTER_API_KEY)."""


def chat_with_model(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
) -> dict:
    """
    Envía mensajes al endpoint de chat de OpenRouter y devuelve {'role', 'content'}.

    - messages: [{'role': 'system'|'user'|'assistant', 'content': str}, ...]
    - model: opcional, sino usa OPENROUTER_DEFAULT_MODEL
    - temperature: creatividad (0-1)
    - max_tokens: opcional, sino usa OPENROUTER_MAX_TOKENS
    """
    api_key = getattr(settings, "OPENROUTER_API_KEY", "")
    if not api_key:
        raise ChatUnavailableError("OPENROUTER_API_KEY no está configurado")

    model_name = model or getattr(settings, "OPENROUTER_DEFAULT_MODEL", DEFAULT_MODEL)
    tok_limit = (
        max_tokens if max_tokens is not None else getattr(settings, "OPENROUTER_MAX_TOKENS", None)
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://uba-assistant.local",
        "X-Title": "UBA Assistant",
    }
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
    }
    if tok_limit is not None:
        payload["max_tokens"] = tok_limit

    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    msg = response.json()["choices"][0]["message"]
    return {
        "role": msg.get("role") or "assistant",
        "content": msg.get("content") or "",
    }
