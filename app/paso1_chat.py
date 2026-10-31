"""PASO 1 · Messages API con system prompt e historial (7 min)

Objetivo: que el agente responda en el chat y recuerde la conversación.
Al terminar, el front muestra la respuesta y el panel Debug muestra stop_reason y tokens.
"""

from app.cliente import MAX_TOKENS, MODEL, client, exigir_completo, resumen_respuesta, resumenes_thinking

# El system prompt es el contrato de comportamiento de toda la sesión: rol, alcance y formato.
SYSTEM_PROMPT = """Eres el asistente de soporte de TiendaTech, una tienda de tecnología en Ecuador.
Responde en español, con calidez y en máximo 4 oraciones.
Si te preguntan por un pedido concreto y no tienes sus datos, dilo y ofrece escalar el caso."""


def texto_de(resp) -> str:
    """Junta el texto de todos los bloques de tipo "text" de una respuesta.

    La respuesta de Claude llega como una LISTA de content blocks (resp.content).
    Puede traer bloques "text", "thinking" o "tool_use", así que hay que filtrar por tipo.
    """
    # TODO 1: recorre resp.content y concatena block.text de los bloques con block.type == "text".
    texto = ...

    exigir_completo(texto, paso=1)
    return texto


def responder(historial: list[dict], opciones: dict) -> dict:
    """Llama a Claude con toda la conversación y devuelve el texto de la respuesta.

    historial: [{"role": "user" | "assistant", "content": "..."}, ...]
    opciones:  parámetros extra que arma el Paso 5 (thinking, effort). Mientras tanto llega vacío.
    """
    # TODO 2: llama a client.messages.create() con estos parámetros:
    #   - model=MODEL y max_tokens=MAX_TOKENS
    #   - system=SYSTEM_PROMPT
    #   - messages=historial   (la API no guarda estado: aquí va TODA la conversación)
    #   - **opciones
    resp = ...

    exigir_completo(resp, paso=1)
    return {
        "texto": texto_de(resp),
        "thinking": resumenes_thinking(resp),
        "debug": [resumen_respuesta(resp, "chat")],
    }
