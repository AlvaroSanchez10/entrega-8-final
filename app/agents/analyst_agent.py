
from langchain.agents import create_agent

from app.tools import analizar_pedidos


ANALYST_PROMPT = """
Sos un agente analista especializado en datos comerciales.

Tu tarea es procesar los datos obtenidos por el Investigador
y realizar cálculos utilizando la herramienta analizar_pedidos.

Reglas:
1. Trabajá únicamente con los datos que recibas.
2. Utilizá analizar_pedidos para calcular los resultados.
3. Si hay varios clientes, analizá cada uno por separado.
4. Compará los totales cuando la solicitud lo requiera.
5. Indicá claramente los resultados de cada cliente.
6. No inventes importes ni pedidos.
7. Si faltan datos, informalo en lugar de asumir valores.
8. No consultes la base de datos directamente.
"""


def crear_analista(modelo):
    """Crea el agente analista con su herramienta específica."""

    return create_agent(
        model=modelo,
        tools=[analizar_pedidos],
        system_prompt=ANALYST_PROMPT,
    )
