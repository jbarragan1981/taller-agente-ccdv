"""PASO 4 · Tool use: el loop del agente (10 min)

Objetivo: convertir el chat del Paso 1 en un agente que consulta pedidos y políticas.
Al terminar, el front muestra cada llamada a herramienta en el panel "Herramientas".

Claude NO ejecuta las herramientas: propone una llamada (bloque tool_use), tu código la ejecuta
y devuelve el resultado (bloque tool_result). El loop sigue mientras stop_reason == "tool_use".
"""

import json

from app.cliente import MAX_TOKENS, MODEL, client, exigir_completo, resumen_respuesta, resumenes_thinking
from app.herramientas import TOOLS, ejecutar_herramienta
from app.paso1_chat import SYSTEM_PROMPT, texto_de

MAX_VUELTAS = 5

SYSTEM_AGENTE = SYSTEM_PROMPT + """
Tienes herramientas para consultar pedidos y políticas. Úsalas antes de responder sobre un
pedido o una política; nunca inventes estados, fechas ni condiciones."""


def agente(historial: list[dict], opciones: dict) -> dict:
    messages = list(historial)
    traza, thinking, debug = [], [], []

    for _ in range(MAX_VUELTAS):
        # SOLUCIÓN TODO 1
        resp = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_AGENTE,
            tools=TOOLS,
            messages=messages,
            **opciones,
        )

        exigir_completo(resp, paso=4)
        debug.append(resumen_respuesta(resp, "agente"))
        thinking += resumenes_thinking(resp)

        # SOLUCIÓN TODO 2 (carry-back): el turno del asistente vuelve completo, thinking incluido.
        messages.append({"role": "assistant", "content": resp.content})

        # SOLUCIÓN TODO 3
        if resp.stop_reason != "tool_use":
            return {"texto": texto_de(resp), "thinking": thinking, "traza": traza, "debug": debug}

        resultados = []
        for bloque in resp.content:
            if bloque.type != "tool_use":
                continue
            # SOLUCIÓN TODO 4
            resultado = ejecutar_herramienta(bloque.name, bloque.input)
            traza.append({"herramienta": bloque.name, "entrada": bloque.input, "resultado": resultado})
            resultados.append({
                "type": "tool_result",
                "tool_use_id": bloque.id,
                "content": json.dumps(resultado, ensure_ascii=False),
                "is_error": "error" in resultado,
            })

        # SOLUCIÓN TODO 5: todos los tool_result de la vuelta en UN mensaje user.
        messages.append({"role": "user", "content": resultados})

    return {
        "texto": "No pude completar la consulta en el número máximo de pasos. ¿Puedes darme más detalles?",
        "thinking": thinking,
        "traza": traza,
        "debug": debug,
    }
