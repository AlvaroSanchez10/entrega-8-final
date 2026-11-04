# Prueba de concurrencia

## Entorno
- Docker Compose
- Python 3.12
- FastAPI + LangGraph + Redis
- Cinco tareas comerciales simultáneas
- Aprobación humana automática mediante endpoint HITL

## Resultados

| Tarea | Estado | Duración |
|---|---|---|
| 1 | COMPLETED | 10.38 s |
| 2 | COMPLETED | 9.08 s |
| 3 | COMPLETED | 8.07 s |
| 4 | COMPLETED | 10.09 s |
| 5 | COMPLETED | 9.06 s |

Tiempo total: 10.40 s

P95 creación de tareas: 0.267 s

P95 duración de tareas: 10.32 s

Tasa de éxito: 5/5 (100%).

## Conclusión

Las cinco solicitudes concurrentes finalizaron correctamente,
incluyendo el proceso de aprobación humana.

La prueba confirma concurrencia funcional en este escenario,
sin constituir una evaluación de carga a gran escala.
