import operator
from typing import Annotated, Literal, NotRequired, TypedDict
from langgraph.graph import MessagesState

class Contribution(TypedDict):
    agent: str
    content: str

class AgentState(MessagesState):
    next_agent: NotRequired[Literal["research", "analyst", "validation"]]
    contributions: Annotated[list[Contribution], operator.add]
    steps: NotRequired[int]
    task_completed: NotRequired[bool]
    validation_passed: NotRequired[bool]
    research_mode: NotRequired[Literal["documentation", "orders", "both"]]
    requires_analysis: NotRequired[bool]
    review_decision: NotRequired[Literal["approved", "rejected"]]
