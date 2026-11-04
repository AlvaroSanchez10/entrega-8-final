import logging
import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


INDEX_NAME = os.getenv(
    "INDEX_NAME",
    "technical-rag-index",
)

EMBEDDING_DIMENSION = 1536
METRIC = "cosine"


def setup_index():
    api_key = os.getenv("PINECONE_API_KEY")

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY no está configurada."
        )

    pc = Pinecone(
        api_key=api_key
    )

    existing_indexes = pc.list_indexes().names()

    if INDEX_NAME in existing_indexes:
        logger.info(
            "El índice '%s' ya existe.",
            INDEX_NAME,
        )

        return pc.Index(INDEX_NAME)

    logger.info(
        "Creando índice Serverless '%s'...",
        INDEX_NAME,
    )

    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric=METRIC,
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        ),
    )

    logger.info(
        "Índice '%s' creado correctamente.",
        INDEX_NAME,
    )

    return pc.Index(INDEX_NAME)


if __name__ == "__main__":
    setup_index()