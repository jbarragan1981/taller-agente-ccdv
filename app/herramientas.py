"""Herramientas del agente: datos simulados de TiendaTech y sus tool schemas. Ya está completo."""

PEDIDOS = {
    "A100": {"estado": "enviado", "transportista": "Servientrega", "entrega_estimada": "2026-11-03"},
    "B200": {"estado": "en preparación", "transportista": None, "entrega_estimada": "2026-11-06"},
    "C300": {"estado": "entregado", "transportista": "Tramaco", "entrega_estimada": "2026-10-28"},
}

POLITICAS = {
    "devoluciones": "Se aceptan devoluciones hasta 30 días después de la entrega, con el producto en su empaque original.",
    "garantia": "Todos los equipos tienen 12 meses de garantía por defectos de fábrica.",
    "envios": "Los envíos dentro de Ecuador tardan de 2 a 5 días hábiles. Galápagos, hasta 10 días.",
    "pagos": "Aceptamos tarjeta de crédito, débito y transferencia. Los cobros duplicados se reversan en 5 a 7 días hábiles.",
}


def consultar_pedido(pedido_id: str) -> dict:
    pedido = PEDIDOS.get(pedido_id.strip().upper())
    if pedido is None:
        return {"error": f"No existe el pedido {pedido_id}. Los códigos tienen una letra y tres números, como A100."}
    return {"pedido_id": pedido_id.upper(), **pedido}


def consultar_politica(tema: str) -> dict:
    return {"tema": tema, "politica": POLITICAS[tema]}


TOOLS = [
    {
        "name": "consultar_pedido",
        "description": (
            "Devuelve el estado, el transportista y la fecha estimada de entrega de un pedido de TiendaTech. "
            "Úsala cuando el cliente pregunte por un pedido concreto y dé su código (por ejemplo A100). "
            "No sirve para políticas generales."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "pedido_id": {"type": "string", "description": "Código del pedido, por ejemplo A100."}
            },
            "required": ["pedido_id"],
            "additionalProperties": False,
        },
    },
    {
        "name": "consultar_politica",
        "description": (
            "Devuelve la política oficial de TiendaTech sobre un tema. Úsala cuando el cliente pregunte por "
            "devoluciones, garantía, tiempos de envío o pagos y cobros. No consulta pedidos individuales."
        ),
        "strict": True,
        "input_schema": {
            "type": "object",
            "properties": {
                "tema": {"type": "string", "enum": ["devoluciones", "garantia", "envios", "pagos"]}
            },
            "required": ["tema"],
            "additionalProperties": False,
        },
    },
]


def ejecutar_herramienta(nombre: str, entrada: dict) -> dict:
    """Ejecuta la herramienta que pidió Claude. Claude propone la llamada; este código la ejecuta."""
    if nombre == "consultar_pedido":
        return consultar_pedido(**entrada)
    if nombre == "consultar_politica":
        return consultar_politica(**entrada)
    return {"error": f"Herramienta desconocida: {nombre}"}
