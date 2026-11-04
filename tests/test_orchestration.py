import asyncio
import json
import os
from types import SimpleNamespace

os.environ.setdefault('OPENAI_API_KEY', 'sk-test-placeholder')

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from app.human_review import human_review_node
from app.state import AgentState
from app.supervisor import supervisor_node
from app.validation import validation_node
from app.graph import route_validation


def contribution(agent, tool):
    return {'agent': agent, 'content': json.dumps({
        'response': 'Datos disponibles', 'tools_executed': [tool]})}


def test_documental_no_requiere_analista():
    state = {'research_mode': 'documentation', 'requires_analysis': False,
             'steps': 1, 'contributions': [contribution('research', 'consultar_documentacion')]}
    result = validation_node(state)
    assert result['validation_passed'] is True
    assert route_validation({**state, **result}) == 'synthesis'


def test_comercial_requiere_analista_cuando_hay_calculos():
    state = {'research_mode': 'orders', 'requires_analysis': True,
             'steps': 1, 'contributions': [contribution('research', 'buscar_pedidos')]}
    result = validation_node(state)
    assert result['validation_passed'] is False
    assert route_validation({**state, **result}) == 'supervisor'


def test_no_pasa_a_sintesis_con_intentos_agotados():
    state = {'research_mode': 'documentation', 'requires_analysis': False,
             'steps': 6, 'contributions': []}
    result = validation_node(state)
    assert result['validation_passed'] is False
    assert route_validation({**state, **result}) == 'failed'


def test_supervisor_no_repite_rag_ni_usa_analista():
    state = {'research_mode': 'documentation', 'requires_analysis': False,
             'steps': 1, 'contributions': [contribution('research', 'consultar_documentacion')]}
    result = asyncio.run(supervisor_node(state))
    assert result['next_agent'] == 'validation'


def test_human_review_real_interrumpe_y_reanuda():
    builder = StateGraph(AgentState)
    builder.add_node('human_review', human_review_node)
    builder.add_edge(START, 'human_review')
    builder.add_edge('human_review', END)
    graph = builder.compile(checkpointer=MemorySaver())
    for approved, expected in [(True, 'approved'), (False, 'rejected')]:
        config = {'configurable': {'thread_id': f'hitl-{expected}'}}
        initial = graph.invoke({'messages': [{'role': 'user', 'content': 'Texto para revisar'}]}, config)
        assert '__interrupt__' in initial
        assert 'human_review' in graph.get_state(config).next
        resumed = graph.invoke(Command(resume={'approved': approved}), config)
        assert resumed['review_decision'] == expected
        assert not graph.get_state(config).next
