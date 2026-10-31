"""PASO 5 · Extended thinking y effort (6 min)

Objetivo: que el interruptor "Pensar" del front active el razonamiento adaptativo.
Al terminar, el panel "Razonamiento" muestra el resumen del thinking y el panel Debug
muestra un bloque "thinking" antes del bloque "text".

- thinking={"type": "adaptive"}: el modelo decide cuánto razonar en cada petición.
- "display": "summarized": el contenido del thinking viene omitido por defecto; así pides un resumen.
- output_config={"effort": "low" | "medium" | "high"}: calibra la profundidad.
  (budget_tokens está deprecado y en los modelos más nuevos devuelve error 400.)
- Los thinking tokens se cobran como output tokens: compara en Debug cuánto sube output_tokens.
"""

from app.cliente import exigir_completo


def opciones_razonamiento(pensar: bool, effort: str) -> dict:
    """Devuelve los parámetros extra que los Pasos 1 y 4 pasan con **opciones."""

    # TODO: si pensar es False, devuelve {}.
    #       si pensar es True, devuelve:
    #         {"thinking": {"type": "adaptive", "display": "summarized"},
    #          "output_config": {"effort": effort}}
    opciones = ...

    exigir_completo(opciones, paso=5)
    return opciones
