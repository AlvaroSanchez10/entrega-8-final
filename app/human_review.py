from langgraph.types import interrupt

def human_review_node(state):
    decision = interrupt({
        "mensaje": "Resultado preparado. Requiere aprobación humana antes de finalizar.",
        "resumen": state["messages"][-1].content,
    })
    if not isinstance(decision, dict) or not isinstance(decision.get("approved"), bool):
        raise ValueError("La revisión requiere una decisión booleana explícita")
    return {"review_decision": "approved" if decision["approved"] else "rejected"}
