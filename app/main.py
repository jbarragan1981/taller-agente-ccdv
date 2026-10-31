"""Servidor FastAPI del taller. Ya está completo: conecta el front con los pasos 1 a 5."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal

import anthropic
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import paso1_chat, paso2_clasificador, paso3_extraccion, paso4_agente, paso5_thinking
from app.cliente import CLAVE_CONFIGURADA, MODEL

STATIC = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="Taller agente CCDV-F")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
pool = ThreadPoolExecutor(max_workers=8)


class Mensaje(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    mensajes: list[Mensaje] = Field(min_length=1, max_length=40)
    pensar: bool = False
    effort: Literal["low", "medium", "high"] = "medium"


@app.get("/")
def inicio():
    return FileResponse(STATIC / "index.html")


@app.get("/api/estado")
def estado():
    return {"clave_configurada": CLAVE_CONFIGURADA, "modelo": MODEL}


def _responder(historial, opciones, pasos):
    """Usa el agente del Paso 4 si está listo; si no, el chat del Paso 1."""
    try:
        r = paso4_agente.agente(historial, opciones)
        pasos["4"] = pasos["1"] = "ok"
        return {**r, "fuente": "paso4"}
    except NotImplementedError:
        pasos["4"] = "pendiente"
    try:
        r = paso1_chat.responder(historial, opciones)
        pasos["1"] = "ok"
        return {**r, "traza": [], "fuente": "paso1"}
    except NotImplementedError:
        pasos["1"] = "pendiente"
        return {
            "texto": "⏳ Todavía no puedo responder: completa el Paso 1 en app/paso1_chat.py.",
            "pendiente": True, "thinking": [], "traza": [], "debug": [], "fuente": None,
        }


def _extraer(texto, pasos):
    try:
        r = paso3_extraccion.extraer_ticket(texto)
        pasos["3"] = "ok"
        return r
    except NotImplementedError:
        pasos["3"] = "pendiente"
        return {"ticket": None, "error": None, "debug": []}


@app.post("/api/chat")
def chat(req: ChatRequest):
    historial = [m.model_dump() for m in req.mensajes]
    if historial[-1]["role"] != "user":
        return JSONResponse(status_code=400, content={"error": "El último mensaje debe ser del usuario."})
    ultimo = historial[-1]["content"]
    pasos = {}

    try:
        opciones = paso5_thinking.opciones_razonamiento(req.pensar, req.effort)
        pasos["5"] = "ok"
    except NotImplementedError:
        opciones = {}
        pasos["5"] = "pendiente"

    try:
        # Las tres tareas son independientes: corren en paralelo para que el chat responda antes.
        f_clas = pool.submit(paso2_clasificador.clasificar, ultimo)
        f_ext = pool.submit(_extraer, ultimo, pasos)
        f_resp = pool.submit(_responder, historial, opciones, pasos)
        clasificacion, extraccion, respuesta = f_clas.result(), f_ext.result(), f_resp.result()
    except anthropic.AuthenticationError:
        return JSONResponse(status_code=401, content={
            "error": "La API key no es válida o no está configurada. Revisa ANTHROPIC_API_KEY y reinicia el servidor."})
    except anthropic.RateLimitError:
        return JSONResponse(status_code=429, content={
            "error": "Límite de peticiones alcanzado (clave compartida). Espera unos segundos y vuelve a enviar."})
    except anthropic.APIStatusError as e:
        return JSONResponse(status_code=502, content={"error": f"Error de la API ({e.status_code}): {e.message}"})
    except anthropic.APIConnectionError:
        return JSONResponse(status_code=502, content={"error": "No hay conexión con la API de Claude."})

    pasos["2"] = "ok" if clasificacion["valida"] else "revisar"
    debug = clasificacion.pop("debug") + extraccion.pop("debug") + respuesta.pop("debug")

    return {
        "respuesta": {"texto": respuesta["texto"], "pendiente": respuesta.get("pendiente", False),
                      "fuente": respuesta["fuente"]},
        "clasificacion": clasificacion,
        "ticket": extraccion,
        "traza": respuesta["traza"],
        "thinking": respuesta["thinking"],
        "debug": debug,
        "pasos": dict(sorted(pasos.items())),
        "mensajes_enviados": len(historial),
    }
