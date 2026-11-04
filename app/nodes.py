import json

from langchain_core.messages import AIMessage, ToolMessage

from app.agents.research_agent import crear_investigador
from app.agents.analyst_agent import crear_analista
from app.llm import crear_modelo
from app.state import AgentState


modelo = crear_modelo()
investigador = crear_investigador(modelo)
analista = crear_analista(modelo)


async def ejecutar_especialista(
    state: AgentState,
    agente,
    nombre: str,
) -> dict:
    """Ejecuta un especialista de manera asíncrona."""

    solicitud_original = state["messages"][0].content
    contribuciones = state.get("contributions", [])

    contexto = "\n".join(
        f"{item['agent']}: {item['content'][:3000]}"
        for item in contribuciones if item["agent"] in ("research", "analyst")
    )

    modo = state.get("research_mode", "no definido")
    especificacion = (
        f"Modo: {modo}. "
        "Utilizá consultar_documentacion para documentos técnicos y buscar_pedidos "
        "para pedidos comerciales; no uses herramientas ajenas a la solicitud."
        if nombre == "research"
        else "Utilizá analizar_pedidos solo para los cálculos solicitados."
    )
    instruccion = (
        f"Solicitud original:\n{solicitud_original}\n\n"
        f"Resultados anteriores:\n{contexto or 'Ninguno'}\n\n"
        f"{especificacion}"
    )

    resultado = await agente.ainvoke({
        "messages": [
            {"role": "user", "content": instruccion}
        ]
    })

    mensajes = resultado["messages"]
    respuesta = mensajes[-1].content

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


async def research_node(state: AgentState) -> dict:
    return await ejecutar_especialista(
        state, investigador, "research"
    )


async def analyst_node(state: AgentState) -> dict:
    return await ejecutar_especialista(
        state, analista, "analyst"
    )
