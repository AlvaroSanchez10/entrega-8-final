
import json

from langchain_core.messages import AIMessage, ToolMessage

from app.agents.research_agent import crear_investigador
from app.agents.analyst_agent import crear_analista
from app.llm import crear_modelo
from app.state import AgentState


modelo = crear_modelo()
investigador = crear_investigador(modelo)
analista = crear_analista(modelo)


def ejecutar_especialista(state: AgentState, agente, nombre: str) -> dict:
    """Ejecuta un especialista y registra su contribución."""

    solicitud_original = state["messages"][0].content
    contribuciones = state.get("contributions", [])

    contexto = "\n".join(
        f"{item['agent']}: {item['content']}"
        for item in contribuciones
    )

    instruccion = (
        f"Solicitud original:\n{solicitud_original}\n\n"
        f"Resultados anteriores:\n{contexto or 'Ninguno'}\n\n"
        "Realizá únicamente tu tarea especializada."
    )

    resultado = agente.invoke({
        "messages": [
            {"role": "user", "content": instruccion}
        ]
    })

    mensajes = resultado["messages"]
    respuesta = mensajes[-1].content

    # Registramos las herramientas realmente ejecutadas.
    herramientas = [
        mensaje.name
        for mensaje in mensajes
        if isinstance(mensaje, ToolMessage)
    ]

    contenido = (
        respuesta
        if isinstance(respuesta, str)
        else json.dumps(respuesta, ensure_ascii=False)
    )

    return {
        "messages": [
            AIMessage(content=contenido, name=nombre)
        ],
        "contributions": [
            {
                "agent": nombre,
                "content": json.dumps(
                    {
                        "response": contenido,
                        "tools_executed": herramientas,
                    },
                    ensure_ascii=False,
                ),
            }
        ],
        "steps": state.get("steps", 0) + 1,
    }


def research_node(state: AgentState) -> dict:
    return ejecutar_especialista(state, investigador, "research")


def analyst_node(state: AgentState) -> dict:
    return ejecutar_especialista(state, analista, "analyst")
