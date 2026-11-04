import json
from typing import Literal
from pydantic import BaseModel, Field
from app.llm import crear_modelo
from app.state import AgentState

MAX_STEPS = 6

class TaskPlan(BaseModel):
    research_mode: Literal["documentation", "orders", "both"] = Field(
        description="Origen de datos necesario: documentos técnicos, pedidos o ambos."
    )
    requires_analysis: bool = Field(
        description="True solo cuando se requieren cálculos sobre pedidos."
    )

def completed_tools(state: AgentState) -> set[str]:
    found = set()
    for item in state.get("contributions", []):
        if item["agent"] not in ("research", "analyst"):
            continue
        try:
            data = json.loads(item["content"])
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict) and str(data.get("response", "")).strip():
            found.update(data.get("tools_executed") or [])
    return found

def required_tools(state: AgentState) -> set[str]:
    mode = state.get("research_mode")
    needed = set()
    if mode in ("documentation", "both"):
        needed.add("consultar_documentacion")
    if mode in ("orders", "both"):
        needed.add("buscar_pedidos")
    if state.get("requires_analysis", False):
        needed.add("analizar_pedidos")
    return needed

async def supervisor_node(state: AgentState) -> dict:
    if state.get("steps", 0) >= MAX_STEPS:
        return {"next_agent": "validation", "task_completed": False}

    mode = state.get("research_mode")
    if mode is None:
        request = state["messages"][0].content
        prompt = f"""Clasificá la solicitud para un sistema con herramientas.
Solicitud: {request}
research_mode= documentation si pregunta sobre FastAPI, Redis, PostgreSQL, Docker o Kubernetes;
orders si busca pedidos comerciales; both si requiere ambos.
requires_analysis=true SOLO si pide calcular totales, promedios o comparar importes de pedidos.
No uses análisis comercial para preguntas técnicas. Respondé únicamente con el esquema."""
        model = crear_modelo().with_structured_output(TaskPlan)
        plan = await model.ainvoke(prompt)
        return {
            "research_mode": plan.research_mode,
            "requires_analysis": plan.requires_analysis if plan.research_mode in ("orders", "both") else False,
            "next_agent": "research",
            "task_completed": False,
        }

    missing = required_tools(state) - completed_tools(state)
    if "consultar_documentacion" in missing or "buscar_pedidos" in missing:
        next_agent = "research"
    elif "analizar_pedidos" in missing:
        next_agent = "analyst"
    else:
        next_agent = "validation"
    return {"next_agent": next_agent, "task_completed": False}
