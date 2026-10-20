from langgraph.types import interrupt


def human_review_node(state):
    decision = interrupt({
        "mensaje": "El análisis terminó. Se requiere aprobación humana antes de finalizar.",
        "resumen": state["messages"][-1].content,
    })

    if decision.get("approved") is not True:
        raise ValueError("La ejecución fue rechazada por el revisor humano.")

    return {}