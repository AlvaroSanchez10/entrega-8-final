
import json

from app.state import AgentState


MAX_STEPS = 6

REQUIRED_TOOLS = {
    "research": "buscar_pedidos",
    "analyst": "analizar_pedidos",
}


def validation_node(state: AgentState) -> dict:
    """Valida que ambos especialistas hayan usado sus herramientas."""

    contributions = state.get("contributions", [])
    errors = []

    for agent_name, required_tool in REQUIRED_TOOLS.items():
        agent_contributions = [
            item
            for item in contributions
            if item["agent"] == agent_name
        ]

        if not agent_contributions:
            errors.append(
                f"Falta la contribución del agente {agent_name}."
            )
            continue

        tool_used = False

        for contribution in agent_contributions:
            try:
                data = json.loads(contribution["content"])
            except (json.JSONDecodeError, TypeError):
                continue

            tools_executed = data.get("tools_executed", [])
            response = data.get("response", "")

            if required_tool in tools_executed and response.strip():
                tool_used = True
                break

        if not tool_used:
            errors.append(
                f"El agente {agent_name} no ejecutó "
                f"correctamente {required_tool}."
            )

    validation_passed = len(errors) == 0
    steps = state.get("steps", 0)

    if validation_passed:
        feedback = "Validación aprobada: ambos agentes ejecutaron sus herramientas."
    else:
        feedback = "Validación fallida: " + " ".join(errors)

    return {
        "validation_passed": validation_passed,
        "task_completed": validation_passed,
        "contributions": [
            {
                "agent": "validation",
                "content": feedback,
            }
        ],
        "next_agent": (
            "synthesis"
            if validation_passed or steps >= MAX_STEPS
            else "research" if any(
                "research" in error for error in errors
            )
            else "analyst"
        ),
    }
