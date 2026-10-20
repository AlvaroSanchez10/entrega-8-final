
import asyncio
import json
import os

from contextlib import asynccontextmanager
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langgraph.checkpoint.redis import RedisSaver
from langgraph.types import Command
from pydantic import BaseModel
from redis.asyncio import Redis

from app.graph import build_graph


load_dotenv(".env")


class TaskRequest(BaseModel):
    prompt: str


class ApprovalRequest(BaseModel):
    approved: bool


background_tasks = set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_url = os.environ["REDIS_URL"]

    app.state.redis = Redis.from_url(
        redis_url,
        decode_responses=True,
    )

    with RedisSaver.from_conn_string(redis_url) as checkpointer:
        checkpointer.setup()

        app.state.graph = build_graph(
            checkpointer=checkpointer
        )

        yield

    await app.state.redis.aclose()


app = FastAPI(
    title="API de Agentes - Pre-entrega 7",
    lifespan=lifespan,
)


def launch_background_task(coroutine):
    task = asyncio.create_task(coroutine)
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


async def save_task(job_id: str, data: dict):
    await app.state.redis.set(
        f"task:{job_id}",
        json.dumps(data, ensure_ascii=False),
    )


async def execute_task(job_id: str, graph_input):
    try:
        await save_task(
            job_id,
            {"status": "RUNNING"},
        )

        config = {
            "configurable": {
                "thread_id": job_id,
            }
        }

        result = await asyncio.to_thread(
            app.state.graph.invoke,
            graph_input,
            config,
        )

        snapshot = await asyncio.to_thread(
            app.state.graph.get_state,
            config,
        )

        if result.get("__interrupt__") or snapshot.next:
            await save_task(
                job_id,
                {
                    "status": "WAITING_APPROVAL",
                    "message": "La tarea espera aprobación humana.",
                },
            )
            return

        messages = result.get("messages", [])

        final_result = (
            str(messages[-1].content)
            if messages
            else "La tarea terminó sin mensajes."
        )

        await save_task(
            job_id,
            {
                "status": "COMPLETED",
                "result": final_result,
            },
        )

    except Exception as error:
        if str(error) == "La ejecución fue rechazada por el revisor humano.":
            await save_task(
                job_id,
                {
                    "status": "REJECTED",
                    "message": str(error),
                },
            )
        else:
            await save_task(
                job_id,
                {
                    "status": "FAILED",
                    "error": str(error),
                },
            )


@app.post("/tasks")
async def create_task(request: TaskRequest):
    job_id = str(uuid4())

    await save_task(
        job_id,
        {"status": "PENDING"},
    )

    launch_background_task(
        execute_task(
            job_id,
            {
                "messages": [
                    {
                        "role": "user",
                        "content": request.prompt,
                    }
                ]
            },
        )
    )

    return {
        "job_id": job_id,
        "status": "PENDING",
    }


@app.get("/tasks/{job_id}")
async def get_task(job_id: str):
    data = await app.state.redis.get(
        f"task:{job_id}"
    )

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada",
        )

    return {
        "job_id": job_id,
        **json.loads(data),
    }


@app.post("/tasks/{job_id}/approve")
async def approve_task(
    job_id: str,
    request: ApprovalRequest,
):
    redis = app.state.redis

    data = await redis.get(f"task:{job_id}")

    if data is None:
        raise HTTPException(
            status_code=404,
            detail="Tarea no encontrada",
        )

    task_data = json.loads(data)

    if task_data["status"] != "WAITING_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail="La tarea no está esperando aprobación.",
        )

    config = {
        "configurable": {
            "thread_id": job_id,
        }
    }

    snapshot = await asyncio.to_thread(
        app.state.graph.get_state,
        config,
    )

    if "human_review" not in snapshot.next:
        raise HTTPException(
            status_code=409,
            detail="No existe una aprobación pendiente en el grafo.",
        )

    await save_task(
        job_id,
        {"status": "RUNNING"},
    )

    launch_background_task(
        execute_task(
            job_id,
            Command(
                resume={
                    "approved": request.approved,
                }
            ),
        )
    )

    return {
        "job_id": job_id,
        "status": "RUNNING",
        "approved": request.approved,
        "message": "Decisión recibida. Reanudando ejecución.",
    }
