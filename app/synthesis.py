
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.llm import crear_modelo
from app.state import AgentState


def synthesis_node(state: AgentState) -> dict:
    """Genera la respuesta final utilizando los resultados validados."""

    if not state.get("validation_passed", False):
        return {
            "messages": [
                AIMessage(
                    content=(
                        "No fue posible completar el análisis "
                        "con todas las verificaciones requeridas. "
                        "Se necesita revisar la información obtenida."
                    ),
                    name="synthesis",
                )
            ],
            "task_completed": False,
        }

    original_request = state["messages"][0].content

    contributions = state.get("contributions", [])

    context = "\n\n".join(
        f"Agente: {item['agent']}\n"
        f"Resultado: {item['content']}"
        for item in contributions
    )

    model = crear_modelo()

    response = model.invoke([
        SystemMessage(
            content=(
                "Sos el sintetizador final de un sistema multiagente. "
                "Respondé de forma clara, precisa y breve. "
                "Utilizá exclusivamente los datos proporcionados "
                "por los especialistas. "
                "No inventes información ni modifiques los cálculos. "
                "Indicá los resultados y la conclusión solicitada."
            )
        ),
        HumanMessage(
            content=(
                f"Solicitud original:\n{original_request}\n\n"
                f"Resultados de los especialistas:\n{context}\n\n"
                "Redactá la respuesta final."
            )
        ),
    ])

    return {
        "messages": [
            AIMessage(
                content=response.content,
                name="synthesis",
            )
        ],
        "task_completed": True,
    }
