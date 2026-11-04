# Evidencias de la entrega final

Proyecto LangSmith: `ai-engineering-trabajo-final`.

## Capturas disponibles

| Archivo | Contenido comprobable |
|---|---|
| [01_integracion_rag_langsmith.png](01_integracion_rag_langsmith.png) | Nodo `research` invoca `consultar_documentacion`, `EnsembleRetriever`, `BM25Retriever` y `VectorStoreRetriever`, con salida documental y tiempos de cada componente. |
| [02_hitl_interrupcion.png](02_hitl_interrupcion.png) | `human_review` interrumpe una tarea después de la síntesis. |
| [03_hitl_reanudacion.png](03_hitl_reanudacion.png) | Segundo turno de LangGraph, `human_review` reanudado y respuesta conservada. El endpoint GET devolvió `COMPLETED` luego de aprobar. |
| [04_rendimiento_antes.png](04_rendimiento_antes.png) | Ejecución previa a optimización, 30,79 s y aprox. 28,91 mil tokens. |
| [05_vista_general_trazas.png](05_vista_general_trazas.png) | Vista del proyecto LangSmith con sus ejecuciones disponibles, incluidas 8,79 s y 30,79 s. |

## Identificadores de trazas verificadas

- Baseline (no optimizada): `01a1a691-6ad7-7361-833a-5d81edbcd5a0` (30,79 s; 20 llamadas LLM; 28.913 tokens; 5 llamadas RAG y 1 `analizar_pedidos`).
- Reanudación baseline: `01a1a697-7625-764f-92ba-3255989a1092`.
- Error anterior de herramienta asíncrona: `01a1a68e-5ca7-710d-92e1-8d95f9a2d4e2` (error esperado durante desarrollo, no prueba exitosa).
- Versión optimizada, ejecución principal: `01a1a6c8-0acb-779e-a62d-1158ab10c9bd` (8,79 s).
- Versión optimizada, reanudación: `01a1a6ca-5001-7696-b581-35c58d23b6b3` (0,03 s).

## Comparación del caso Redis

| Indicador | Versión anterior | Versión consolidada |
|---|---:|---:|
| Llamadas al modelo | 20 | 4 |
| Tokens del modelo | 28.913 | 3.509 |
| Herramientas RAG | 5 | 1 |
| Herramientas comerciales innecesarias | 1 | 0 |
| Duración trazada | 30,79 s (principal) | 8,79 s (principal) + 0,03 s (reanudación) |

**Alcance de la medición:** comparación de dos ejecuciones puntuales de la misma solicitud, no un promedio ni una prueba de carga. El tiempo de espera para aprobación humana no se incluye. Evitar considerar la suma como latencia extremo a extremo.

## Cobertura y pendientes

La carpeta contiene **cinco capturas**, no cinco trazas independientes. Para cumplir un requisito estricto de **cinco ejecuciones trazadas**, se debe documentar la selección final de cinco trazas distintas desde LangSmith con identificación de caso, entrada, resultado, tokens y latencia. Varias trazas actuales provienen de pruebas locales automatizadas sin LLM y no reemplazan por sí solas los escenarios requeridos. Las pruebas `pytest` validaron 13 casos en Docker; eso es evidencia separada y puede capturarse desde la terminal si el evaluador lo solicita.

No se debe afirmar que existe evidencia gráfica de **rechazo humano en producción** o **concurrencia real** solo a partir de estas capturas. Esos escenarios requieren prueba documental específica o datos del test correspondiente.
