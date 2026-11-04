import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from app.llm import crear_modelo
from app.state import AgentState

async def synthesis_node(state: AgentState) -> dict:
    if not state.get("validation_passed", False):
        raise ValueError("La síntesis requiere validación aprobada")
    original = state["messages"][0].content
    context = "\n\n".join(
        f"Agente: {item['agent']}\nResultado: {item['content']}"
        for item in state.get("contributions", []) if item["agent"] in ("research", "analyst")
    )
    response = await crear_modelo().ainvoke([
        SystemMessage(content=(
            "Redactá una respuesta breve y precisa usando solo las evidencias provistas. "
            "Si citás documentos, indicá sus nombres de archivo. "
            "No inventes resultados comerciales ni datos técnicos."
        )),
        HumanMessage(content=f"Solicitud:\n{original}\n\nEvidencia:\n{context}\n\nRespuesta:"),
    ])
    content = response.content if isinstance(response.content, str) else json.dumps(response.content, ensure_ascii=False)
    return {"messages": [AIMessage(content=content, name="synthesis")], "task_completed": True}
