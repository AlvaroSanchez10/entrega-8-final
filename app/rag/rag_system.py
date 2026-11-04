import logging
import time

from app.rag.retriever import create_hybrid_retriever
from app.rag.schemas import RetrievedDocument


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


TOP_K = 5


class RAGSystem:

    def __init__(self):
        logger.info(
            "Inicializando recuperador híbrido..."
        )

        self.retriever = create_hybrid_retriever()

        logger.info(
            "Recuperador híbrido listo."
        )

    async def retrieve(
        self,
        query: str,
    ) -> list[RetrievedDocument]:

        start_time = time.perf_counter()

        logger.info(
            "Iniciando recuperación para consulta: %s",
            query,
        )

        documents = await self.retriever.ainvoke(query)

        results = []

        for document in documents[:TOP_K]:

            metadata = document.metadata

            result = RetrievedDocument(
                document_id=metadata.get(
                    "id",
                    metadata.get(
                        "source",
                        "unknown",
                    ),
                ),
                content=document.page_content,
                source=metadata.get(
                    "source",
                    "unknown",
                ),
                category=metadata.get(
                    "category",
                    "general",
                ),
                score=None,
                retrieval_type="hybrid",
            )

            results.append(
                result
            )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "Recuperación completada en %.3f segundos.",
            elapsed,
        )

        logger.info(
            "Se devolvieron %s documentos.",
            len(results),
        )

        return results