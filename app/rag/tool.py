
import asyncio
import json

from langchain_core.tools import tool

from app.rag.rag_system import RAGSystem


_rag_system = None
_rag_lock = asyncio.Lock()


async def get_rag_system() -> RAGSystem:
    global _rag_system

    if _rag_system is None:
        async with _rag_lock:
            if _rag_system is None:
                _rag_system = await asyncio.to_thread(
                    RAGSystem
                )

    return _rag_system


@tool
async def consultar_documentacion(consulta: str) -> str:
    """
    Busca información técnica en documentos mediante RAG
    híbrido BM25 + Pinecone.

    Utilizar para consultas sobre FastAPI, Redis,
    PostgreSQL, Docker y Kubernetes.
    """
    rag = await get_rag_system()

    documentos = await rag.retrieve(consulta)

    resultados = [
        {
            "contenido": documento.content,
            "fuente": documento.source,
            "categoria": documento.category,
        }
        for documento in documentos
    ]

    return json.dumps(
        resultados,
        ensure_ascii=False,
    )
