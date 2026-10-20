import json
import math
from pathlib import Path

from langchain_core.tools import tool


DATA_PATH = Path(__file__).resolve().parent / "data" / "orders.json"


@tool
def buscar_pedidos(cliente_id: int) -> str:
    """Busca los pedidos de un cliente por su ID y devuelve sus datos."""

    with open(DATA_PATH, "r", encoding="utf-8") as archivo:
        pedidos = json.load(archivo)

    resultados = [
        pedido
        for pedido in pedidos
        if pedido["customer_id"] == cliente_id
    ]

    if not resultados:
        return f"No se encontraron pedidos para el cliente {cliente_id}."

    return json.dumps(resultados, ensure_ascii=False, indent=2)

@tool
def analizar_pedidos(importes: list[float]) -> dict:
    """Calcula el total, la cantidad y el promedio de una lista de importes de pedidos."""

    if not importes:
        return {
            "cantidad": 0,
            "total": 0,
            "promedio": 0,
        }

    if any(
        not isinstance(importe, (int, float))
        or isinstance(importe, bool)
        or not math.isfinite(importe)
        or importe < 0
        for importe in importes
    ):
        raise ValueError("Los importes deben ser números finitos y no negativos.")

    total = round(sum(importes), 2)
    promedio = round(total / len(importes), 2)

    return {
        "cantidad": len(importes),
        "total": total,
        "promedio": promedio,
    }
