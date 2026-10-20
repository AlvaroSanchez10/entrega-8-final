
from typing import Literal

from pydantic import BaseModel, Field

from app.llm import crear_modelo
from app.state import AgentState


MAX_STEPS = 6


class SupervisorDecision(BaseModel):
    next_agent: Literal["research", "analyst", "validation"] = Field(
        description="Próximo nodo que debe ejecutarse"
    )
    reason: str = Field(
        description="Motivo de la decisión"
    )


def supervisor_node(state: AgentState) -> dict:
    """Decide qué especialista debe intervenir."""

    steps = state.get("steps", 0)
    contributions = state.get("contributions", [])

    # Evitamos ciclos infinitos.
    if steps >= MAX_STEPS:
        return {
            "next_agent": "validation",
            "task_completed": False,
        }

    # Conservamos la solicitud original del usuario.
    original_request = state["messages"][0].content

    # Preparamos un resumen de las contribuciones.
    contributions_text = "\n".join(
        f"{item['agent']}: {item['content']}"
        for item in contributions
    ) or "Todavía no hay contribuciones."

    prompt = f"""
Sos el Supervisor de un sistema multiagente comercial.

Solicitud original:
{original_request}

Contribuciones de los especialistas:
{contributions_text}

Especialistas disponibles:
- research: busca pedidos reales en la base de datos.
- analyst: realiza cálculos y compara resultados.
- validation: comprueba los resultados antes de finalizar.

Reglas:
1. Si faltan datos de pedidos, elegí research.
2. Si ya hay datos pero faltan cálculos, elegí analyst.
3. Si los datos y cálculos están completos, elegí validation.
4. Si un especialista no cumplió su tarea, podés volver a elegirlo.
5. No repitas tareas que ya estén completas.
6. Nunca inventes información.
"""

    model = crear_modelo().with_structured_output(
        SupervisorDecision
    )

    decision = model.invoke(prompt)

    return {
        "next_agent": decision.next_agent,
        "task_completed": False,
    }
