
import operator
from typing import Annotated, Literal, TypedDict

from langgraph.graph import MessagesState


class Contribution(TypedDict):
    agent: str
    content: str


class AgentState(MessagesState):
    next_agent: Literal["research", "analyst", "validation", "synthesis", "FINISH"]
    contributions: Annotated[list[Contribution], operator.add]
    steps: int
    task_completed: bool
    validation_passed: bool
