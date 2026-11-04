import logging
import os
import re
import time
from pathlib import Path

import tiktoken
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone

from app.rag.schemas import DocumentMetadata


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


DATA_DIR = Path(__file__).resolve().parent / "data"

INDEX_NAME = os.getenv(
    "INDEX_NAME",
    "technical-rag-index",
)

NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "dev",
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = 600
CHUNK_OVERLAP = 80

BATCH_SIZE = 100


CATEGORY_BY_FILE = {
    "fastapi.md": "backend",
    "redis.md": "database",
    "postgresql.md": "database",
    "docker.md": "devops",
    "kubernetes.md": "devops",
}


def clean_text(text: str) -> str:
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    return text.strip()


def get_token_length(text: str) -> int:
    encoding = tiktoken.get_encoding(
        "cl100k_base"
    )

    return len(
        encoding.encode(text)
    )


def load_documents() -> list[dict]:
    documents = []

    for file_path in DATA_DIR.glob("*"):

        if file_path.suffix not in {
            ".txt",
            ".md",
        }:
            continue

        content = file_path.read_text(
            encoding="utf-8"
        )

        content = clean_text(content)

        category = CATEGORY_BY_FILE.get(
            file_path.name,
            "general",
        )

        documents.append(
            {
                "source": file_path.name,
                "content": content,
                "category": category,
            }
        )

    logger.info(
        "Se cargaron %s documentos.",
        len(documents),
    )

    return documents


def split_documents(
    documents: list[dict],
) -> list[dict]:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=get_token_length,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = []

    for document in documents:

        parts = splitter.split_text(
            document["content"]
        )

        for index, part in enumerate(parts):

            metadata = DocumentMetadata(
                source=document["source"],
                page=1,
                category=document["category"],
                namespace=NAMESPACE,
                text=part,
            )

            chunks.append(
                {
                    "id": (
                        f"{document['source']}"
                        f"-chunk-{index}"
                    ),
                    "text": part,
                    "metadata": metadata,
                }
            )

    logger.info(
        "Se generaron %s chunks.",
        len(chunks),
    )

    return chunks


def prepare_vectors(
    chunks: list[dict],
) -> list[dict]:

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=os.getenv(
            "OPENAI_API_KEY"
        ),
    )

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    logger.info(
        "Generando embeddings para %s chunks...",
        len(texts),
    )

    vectors = embeddings.embed_documents(
        texts
    )

    pinecone_vectors = []

    for chunk, vector in zip(
        chunks,
        vectors,
    ):

        pinecone_vectors.append(
            {
                "id": chunk["id"],
                "values": vector,
                "metadata": (
                    chunk["metadata"]
                    .model_dump()
                ),
            }
        )

    return pinecone_vectors


def upsert_in_batches(
    index,
    vectors: list[dict],
):
    total = len(vectors)

    for start in range(
        0,
        total,
        BATCH_SIZE,
    ):

        end = min(
            start + BATCH_SIZE,
            total,
        )

        batch = vectors[
            start:end
        ]

        logger.info(
            "Subiendo batch %s-%s de %s...",
            start + 1,
            end,
            total,
        )

        index.upsert(
            vectors=batch,
            namespace=NAMESPACE,
        )

    logger.info(
        "Todos los batches fueron enviados."
    )


def ingest_documents():

    start_time = time.perf_counter()

    api_key = os.getenv(
        "PINECONE_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY no está configurada."
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            "OPENAI_API_KEY no está configurada."
        )

    pc = Pinecone(
        api_key=api_key
    )

    index = pc.Index(
        INDEX_NAME
    )

    documents = load_documents()

    if not documents:
        logger.warning(
            "No se encontraron documentos "
            "en la carpeta data."
        )

        return

    chunks = split_documents(
        documents
    )

    vectors = prepare_vectors(
        chunks
    )

    upsert_in_batches(
        index,
        vectors,
    )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    logger.info(
        "Ingesta completada en %.2f segundos.",
        elapsed,
    )


if __name__ == "__main__":
    ingest_documents()