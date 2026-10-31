"""Cliente de Anthropic y utilidades compartidas. Este archivo ya está completo."""

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
MAX_TOKENS = 4000
CLAVE_CONFIGURADA = bool(os.getenv("ANTHROPIC_API_KEY"))

# max_retries: el SDK reintenta solo los errores 429 (rate limit) y 5xx con espera exponencial.
# En el taller compartimos una clave, por eso subimos los reintentos.
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY") or "falta-configurar-la-clave",
    max_retries=6,
)


def exigir_completo(valor, paso: int):
    """Avisa al servidor que un paso todavía tiene un `...` sin reemplazar."""
    if valor is Ellipsis:
        raise NotImplementedError(f"Paso {paso} pendiente")


def resumen_respuesta(resp, llamada: str) -> dict:
    """Datos de una respuesta para el panel de depuración del front."""
    return {
        "llamada": llamada,
        "stop_reason": resp.stop_reason,
        "input_tokens": resp.usage.input_tokens,
        "output_tokens": resp.usage.output_tokens,
        "bloques": [bloque.type for bloque in resp.content],
    }


def resumenes_thinking(resp) -> list[str]:
    """Textos de los bloques thinking (solo llegan si se pidió display: summarized)."""
    return [
        bloque.thinking
        for bloque in resp.content
        if bloque.type == "thinking" and getattr(bloque, "thinking", "")
    ]
