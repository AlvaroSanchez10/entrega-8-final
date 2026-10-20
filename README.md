# entrega-7-api-agentes
# Pre-entrega 7 | API de agentes con LangGraph

Sistema multiagente desarrollado en Python que expone una API REST con FastAPI, ejecuta tareas en segundo plano, utiliza Redis para persistencia de estados y checkpoints, incorpora aprobación humana (HITL) y registra trazas mediante LangSmith.

## 1. Tecnologías utilizadas

- **Python:** lenguaje principal.
- **LangGraph:** orquestación del flujo multiagente.
- **LangChain y OpenAI:** integración de modelos de lenguaje y herramientas.
- **FastAPI:** API REST para gestionar tareas.
- **Redis Stack:** almacenamiento de estados y checkpoints mediante RedisSaver.
- **LangSmith:** observabilidad, trazas, tiempos, tokens y costos.
- **Docker Compose:** ejecución de Redis.
- **HTTPX:** pruebas de solicitudes concurrentes.

## 2. Arquitectura

El sistema utiliza un grafo de agentes especializados:

- **Supervisor:** determina qué agente debe intervenir.
- **Research:** consulta los pedidos mediante `buscar_pedidos`.
- **Analyst:** calcula cantidad, total y promedio mediante `analizar_pedidos`.
- **Validation:** comprueba que los agentes hayan ejecutado sus herramientas.
- **Synthesis:** construye la respuesta final.
- **Human Review:** interrumpe la ejecución para solicitar aprobación humana.

Flujo general:

```text
POST /tasks
     |
     v
 Supervisor
     |
     +--> Research ----+
     |                 |
     +--> Analyst -----+--> Supervisor
     |                        |
     +<-----------------------+
     |
     v
 Validation
     |
     +--> Supervisor (si necesita correcciones)
     |
     v
 Synthesis
     |
     v
 Human Review
     |
     +--> WAITING_APPROVAL
              |
              v
       POST /tasks/{job_id}/approve
              |
              +--> Aprobación: COMPLETED
              |
              +--> Rechazo: REJECTED
```

## 3. Instalación

Clonar el repositorio:

```bash
git clone https://github.com/AlvaroSanchez10/entrega-7-api-agentes.git
cd entrega-7-api-agentes
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

Crear un archivo `.env` en la raíz del proyecto:

```dotenv
OPENAI_API_KEY=tu_clave_de_openai
OPENAI_MODEL=gpt-4.1-mini

REDIS_URL=redis://localhost:6379/0

LANGSMITH_TRACING=true
LANGSMITH_API_KEY=tu_clave_de_langsmith
LANGSMITH_PROJECT=entrega-7-agentes
```

Las API Keys son privadas. El archivo `.env` no debe publicarse en GitHub.

## 4. Iniciar Redis

El proyecto utiliza Redis Stack para almacenar los estados de las tareas y los checkpoints de LangGraph.

Iniciar el servicio:

```bash
docker compose up -d
```

Verificar la conexión:

```bash
docker compose exec redis redis-cli ping
```

Resultado esperado:

```text
PONG
```

## 5. Iniciar FastAPI

Ejecutar:

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

La documentación interactiva estará disponible en:

http://localhost:8000/docs

Redis debe encontrarse activo antes de iniciar la API.

## 6. Endpoints

### POST /tasks

Recibe una solicitud y devuelve inmediatamente un identificador de tarea.

Ejemplo:

```json
{
  "prompt": "Consulta los pedidos del cliente con ID 102 usando buscar_pedidos. Luego utiliza analyst y analizar_pedidos para calcular cantidad, total y promedio. Finalmente, valida los resultados."
}
```

Respuesta inicial:

```json
{
  "job_id": "identificador-uuid",
  "status": "PENDING"
}
```

La ejecución continúa en segundo plano.

### GET /tasks/{job_id}

Consulta el estado actual de una tarea.

Estados contemplados:

- `PENDING`: tarea recibida.
- `RUNNING`: ejecución en curso.
- `WAITING_APPROVAL`: pendiente de aprobación humana.
- `COMPLETED`: ejecución finalizada.
- `REJECTED`: rechazo del revisor humano.
- `FAILED`: error durante la ejecución.

### POST /tasks/{job_id}/approve

Permite aprobar o rechazar una tarea pausada.

Para aprobar:

```json
{
  "approved": true
}
```

Para rechazar:

```json
{
  "approved": false
}
```

La reanudación se implementa mediante `Command(resume=...)` de LangGraph.

## 7. Persistencia con Redis

El proyecto utiliza Redis para dos propósitos:

**Estados de tareas:** cada ejecución tiene un `job_id` único que permite consultar su estado mediante FastAPI.

**Checkpoints de LangGraph:** RedisSaver conserva el estado del grafo utilizando el mismo identificador como `thread_id`.

Esto permite recuperar el estado de una ejecución y reanudar tareas interrumpidas por aprobación humana.

## 8. Human-in-the-Loop (HITL)

El nodo `human_review` utiliza `interrupt()` para suspender el grafo antes de su finalización.

Durante la pausa:

1. LangGraph conserva su estado en Redis.
2. La API registra `WAITING_APPROVAL`.
3. El usuario envía una decisión al endpoint de aprobación.
4. LangGraph continúa utilizando `Command(resume=...)`.

Se realizaron pruebas de aprobación y rechazo.

La aprobación permitió continuar hasta `COMPLETED`. El rechazo también fue procesado correctamente y se implementó una clasificación diferenciada mediante `REJECTED`.

## 9. Observabilidad con LangSmith

Se configuró LangSmith mediante variables de entorno para registrar las ejecuciones del sistema.

Las trazas permiten inspeccionar:

- Llamadas al modelo de lenguaje.
- Ejecución de agentes y herramientas.
- Duración de las operaciones.
- Tokens utilizados.
- Costo estimado de las llamadas al modelo.

El proyecto utiliza el nombre `entrega-7-agentes` para organizar las trazas.

## 10. Prueba de concurrencia

Se implementó `test_concurrencia.py` para enviar cinco solicitudes simultáneas a FastAPI utilizando HTTPX.

Con Redis y FastAPI en funcionamiento, ejecutar:

```bash
python test_concurrencia.py
```

El script registra el tiempo de respuesta HTTP, el tiempo hasta la finalización de cada tarea y los percentiles p95.

### Resultados obtenidos

| Métrica | Resultado |
|---|---|
| Solicitudes concurrentes | 5 |
| Tareas completadas | 5/5 |
| Duración global | 14,67 segundos |
| P95 respuesta POST | 0,046 segundos |
| P95 ejecución completa | 14,66 segundos |

Las cinco tareas finalizaron con estado `COMPLETED`.

La duración global y el p95 indican que las ejecuciones pudieron desarrollarse concurrentemente.

**Nota metodológica:** el p95 se calculó mediante interpolación lineal a partir de cinco observaciones. Los tiempos de ejecución completa incluyen el intervalo de consulta periódica de estados, aproximadamente de un segundo. Estas mediciones corresponden a una prueba puntual y no constituyen un benchmark exhaustivo de producción.

## 11. Evidencias

Las capturas de pantalla de las pruebas se organizan en la carpeta `screenshots/`.

Evidencias previstas:

- Trazas de ejecución en LangSmith, incluyendo tokens y costos.
- Resultados de la prueba de concurrencia y latencias p95.
- Tarea pausada en estado `WAITING_APPROVAL`.
- Aprobación humana mediante Swagger.
- Finalización correcta en `COMPLETED`.
- Rechazo humano y resultado correspondiente.

## 12. Limitaciones y mejoras futuras

Esta implementación demuestra las funcionalidades centrales de la pre-entrega. Para un despliegue de producción se recomienda incorporar autenticación, autorización de revisores, control de aprobaciones simultáneas, recuperación automática de trabajos pendientes tras reinicios, una cola persistente de tareas y pruebas de carga más extensas.

También sería conveniente sustituir la identificación textual de rechazos por decisiones estructuradas dentro del grafo.

## 13. Autor

**Álvaro Sánchez**

Proyecto desarrollado para la Pre-entrega 7 de AI Engineering, Coderhouse.