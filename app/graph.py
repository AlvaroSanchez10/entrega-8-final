from typing import Literal

from langgraph.graph import StateGraph, START, END

from app.state import AgentState
from app.supervisor import supervisor_node
from app.nodes import research_node, analyst_node
from app.validation import validation_node
from app.synthesis import synthesis_node
from app.human_review import human_review_node


def route_supervisor(
    state: AgentState,
) -> Literal["research", "analyst", "validation"]:
    """Envía el trabajo al nodo elegido por el Supervisor."""
    return state["next_agent"]


def route_validation(
    state: AgentState,
) -> Literal["supervisor", "synthesis"]:
    """Permite corregir resultados o finalizar el proceso."""
    if state.get("validation_passed", False):
        return "synthesis"

    if state.get("steps", 0) >= 6:
        return "synthesis"

    return "supervisor"


def build_graph(checkpointer=None):
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("validation", validation_node)
    workflow.add_node("synthesis", synthesis_node)
    workflow.add_node("human_review", human_review_node)

    workflow.add_edge(START, "supervisor")

    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "research": "research",
            "analyst": "analyst",
            "validation": "validation",
        },
    )

    workflow.add_edge("research", "supervisor")
    workflow.add_edge("analyst", "supervisor")

    workflow.add_conditional_edges(
        "validation",
        route_validation,
        {
            "supervisor": "supervisor",
            "synthesis": "synthesis",
        },
    )

    workflow.add_edge("synthesis", "human_review")
    workflow.add_edge("human_review", END)

    return workflow.compile(checkpointer=checkpointer)