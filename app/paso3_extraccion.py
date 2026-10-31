"""PASO 3 · Structured outputs: el formato lo garantiza la API (10 min)

Objetivo: extraer un ticket estructurado de cada mensaje. Al terminar, el front muestra la
tarjeta "Ticket" con cliente, categoría, prioridad y resumen.

Con output_config.format la API aplica constrained decoding: en cada token solo permite los que
mantienen la salida válida contra el JSON schema. Aun así, una respuesta cortada (max_tokens) o
rechazada (refusal) NO cumple el schema, por eso hay que revisar stop_reason antes de parsear.
"""

import json

from app.cliente import MODEL, client, exigir_completo, resumen_respuesta
from app.paso1_chat import texto_de

# Para probar el TODO 2, baja este valor a 20 y escribe un mensaje largo.
MAX_TOKENS_EXTRACCION = 600

SYSTEM_EXTRACCION = """Extrae los datos del mensaje de soporte dentro de <ticket>.
Si el mensaje es un saludo o no describe un problema, marca es_ticket como false.
Si un dato no aparece, usa null. Si mezcla un cobro con una falla técnica, la categoría es ESCALATION."""

# Fíjate en tres decisiones del schema:
#   - enum fija los valores permitidos
#   - anyOf con null define qué pasa cuando el dato no aparece
#   - additionalProperties: false impide campos inventados
SCHEMA_TICKET = {
    "type": "object",
    "properties": {
        "es_ticket": {"type": "boolean"},
        "cliente": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "pedido_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "categoria": {"type": "string", "enum": ["BILLING", "TECHNICAL", "ESCALATION"]},
        "prioridad": {"type": "string", "enum": ["baja", "media", "alta"]},
        "resumen": {"type": "string", "description": "Una oración de máximo 20 palabras."},
    },
    "required": ["es_ticket", "cliente", "pedido_id", "categoria", "prioridad", "resumen"],
    "additionalProperties": False,
}


def extraer_ticket(texto: str) -> dict:
    """Devuelve {"ticket": dict | None, "error": str | None, "debug": [...]}."""

    # SOLUCIÓN TODO 1
    resp = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_EXTRACCION,
        system=SYSTEM_EXTRACCION,
        messages=[{"role": "user", "content": f"<ticket>{texto}</ticket>"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA_TICKET}},
    )

    exigir_completo(resp, paso=3)
    debug = [resumen_respuesta(resp, "extraccion")]

    # SOLUCIÓN TODO 2: un schema garantizado no es un éxito garantizado.
    if resp.stop_reason in ("max_tokens", "refusal"):
        return {"ticket": None, "error": f"stop_reason={resp.stop_reason}", "debug": debug}

    # SOLUCIÓN TODO 3
    ticket = json.loads(texto_de(resp))

    exigir_completo(ticket, paso=3)
    return {"ticket": ticket, "error": None, "debug": debug}
