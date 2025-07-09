from openai import OpenAI
from django.conf import settings

# 1) Carga segura de la API key
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY no está configurado en settings.py "
        "(ej. OPENAI_API_KEY = 'tu_token')"
    )

# 2) Instancia del cliente moderno
client = OpenAI(api_key=OPENAI_API_KEY)

# 3) Fallback para modelo y max_tokens
DEFAULT_MODEL      = getattr(settings, 'OPENAI_DEFAULT_MODEL', 'gpt-3.5-turbo')
DEFAULT_MAX_TOKENS = getattr(settings, 'OPENAI_MAX_TOKENS', None)

def chat_with_gpt(
    messages: list[dict],
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = None
) -> dict:
    """
    Envía mensajes a OpenAI chat.completions.create y devuelve {'role','content'}.

    - messages: [{'role': 'system'|'user'|'assistant', 'content': str}, ...]
    - model: opcional, sino usa DEFAULT_MODEL
    - temperature: creatividad (0–1)
    - max_tokens: opcional, sino usa DEFAULT_MAX_TOKENS
    """
    model_name = model or DEFAULT_MODEL
    tok_limit  = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS

    payload = {
        "model":       model_name,
        "messages":    messages,
        "temperature": temperature,
    }
    if tok_limit is not None:
        payload["max_tokens"] = tok_limit

    response = client.chat.completions.create(**payload)
    msg = response.choices[0].message  # objeto con .role y .content

    return {
        "role":    msg.role,
        "content": msg.content,
    }
