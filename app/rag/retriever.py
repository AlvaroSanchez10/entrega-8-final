import logging
import os

from dotenv import load_dotenv
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from app.rag.ingest import load_documents, split_documents


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

NAMESPACE = os.getenv(
    "PINECONE_NAMESPACE",
    "dev",
)

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

TOP_K = 5


def build_local_documents() -> list[Document]:
    raw_documents = load_documents()

    chunks = split_documents(
        raw_documents
    )

    documents = []

    for chunk in chunks:
        documents.append(
            Document(
                page_content=chunk["text"],
                metadata={
                    "id": chunk["id"],
                    "source": (
                        chunk["metadata"].source
                    ),
                    "category": (
                        chunk["metadata"].category
                    ),
                },
            )
        )

    logger.info(
        "Se prepararon %s chunks "
        "para el recuperador BM25.",
        len(documents),
    )

    return documents


def create_bm25_retriever():
    documents = build_local_documents()

    retriever = BM25Retriever.from_documents(
        documents
    )

    retriever.k = TOP_K

    return retriever


def create_vector_retriever():
    api_key = os.getenv(
        "PINECONE_API_KEY"
    )

    openai_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        raise ValueError(
            "PINECONE_API_KEY no está configurada."
        )

    if not openai_key:
        raise ValueError(
            "OPENAI_API_KEY no está configurada."
        )

    pc = Pinecone(
        api_key=api_key
    )

    index = pc.Index(
        INDEX_NAME
    )

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=openai_key,
    )

    vector_store = PineconeVectorStore(
        index=index,
        embedding=embeddings,
        namespace=NAMESPACE,
        text_key="text",
    )

    retriever = vector_store.as_retriever(
        search_kwargs={
            "k": TOP_K,
        }
    )

    return retriever


def create_hybrid_retriever():
    bm25_retriever = (
        create_bm25_retriever()
    )

    vector_retriever = (
        create_vector_retriever()
    )

    hybrid_retriever = EnsembleRetriever(
        retrievers=[
            bm25_retriever,
            vector_retriever,
        ],
        weights=[
            0.4,
            0.6,
        ],
    )

    logger.info(
        "Recuperador híbrido creado: "
        "BM25=0.4 | Vectorial=0.6"
    )

    return hybrid_retriever