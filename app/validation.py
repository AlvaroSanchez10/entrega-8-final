from app.state import AgentState
from app.supervisor import MAX_STEPS, completed_tools, required_tools

def validation_node(state: AgentState) -> dict:
    mode = state.get("research_mode")
    available = completed_tools(state)
    missing = sorted(required_tools(state) - available)
    errors = []
    if mode not in ("documentation", "orders", "both"):
        errors.append("Plan de investigación ausente o inválido")
    if missing:
        errors.append("Herramientas faltantes: " + ", ".join(missing))
    passed_validation = not errors
    exhausted = state.get("steps", 0) >= MAX_STEPS
    feedback = (
        "Validación aprobada: evidencia de herramientas requerida presente."
        if passed_validation else "Validación fallida: " + "; ".join(errors)
    )
    if not passed_validation and exhausted:
        feedback += ". Se agotó el límite de intentos; no se genera respuesta aprobable."
    return {
        "validation_passed": passed_validation,
        "task_completed": passed_validation,
        "contributions": [{"agent": "validation", "content": feedback}],
    }
