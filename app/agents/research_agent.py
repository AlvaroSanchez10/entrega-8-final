
from langchain.agents import create_agent

from app.tools import buscar_pedidos


RESEARCH_PROMPT = """
Sos un agente investigador especializado en pedidos comerciales.

Tu tarea es buscar información en la base de datos utilizando
la herramienta buscar_pedidos.

Reglas:
1. Consultá la herramienta para obtener datos reales.
2. Si la solicitud menciona varios clientes, consultá cada uno.
3. Conservá los IDs, importes y números de pedido.
4. No inventes información que no aparezca en la herramienta.
5. No realices cálculos de totales ni promedios.
6. Presentá los datos de forma clara para el agente Analista.
"""


def crear_investigador(modelo):
    """Crea el agente investigador con su herramienta específica."""

    return create_agent(
        model=modelo,
        tools=[buscar_pedidos],
        system_prompt=RESEARCH_PROMPT,
    )
