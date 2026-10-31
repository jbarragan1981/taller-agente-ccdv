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
        # TODO 1: llama a client.messages.create() igual que en el Paso 1, pero con
        #   system=SYSTEM_AGENTE, tools=TOOLS y messages=messages (más **opciones).
        resp = ...

        exigir_completo(resp, paso=4)
        debug.append(resumen_respuesta(resp, "agente"))
        thinking += resumenes_thinking(resp)

        # TODO 2 (regla de carry-back): agrega a messages el turno del asistente COMPLETO,
        #   tal como llegó: {"role": "assistant", "content": resp.content}
        #   Si filtras los bloques thinking, la API rechaza la siguiente llamada.

        # TODO 3: si resp.stop_reason != "tool_use", Claude ya terminó:
        #   return {"texto": texto_de(resp), "thinking": thinking, "traza": traza, "debug": debug}

        resultados = []
        for bloque in resp.content:
            if bloque.type != "tool_use":
                continue
            # TODO 4: para cada bloque tool_use:
            #   a) resultado = ejecutar_herramienta(bloque.name, bloque.input)
            #   b) traza.append({"herramienta": bloque.name, "entrada": bloque.input, "resultado": resultado})
            #   c) resultados.append({
            #          "type": "tool_result",
            #          "tool_use_id": bloque.id,            # empareja el resultado con su llamada
            #          "content": json.dumps(resultado, ensure_ascii=False),
            #          "is_error": "error" in resultado,    # avisa a Claude que la herramienta falló
            #      })

        # TODO 5: agrega UN solo mensaje user con TODOS los tool_result de esta vuelta:
        #   {"role": "user", "content": resultados}

    return {
        "texto": "No pude completar la consulta en el número máximo de pasos. ¿Puedes darme más detalles?",
        "thinking": thinking,
        "traza": traza,
        "debug": debug,
    }
