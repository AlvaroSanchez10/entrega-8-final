from typing import Literal

from pydantic import BaseModel, Field, field_validator


class DocumentMetadata(BaseModel):
    source: str = Field(
        min_length=1,
        description="Nombre o ruta del documento de origen.",
    )

    page: int = Field(
        ge=0,
        description="Número de página o sección del documento.",
    )

    category: str = Field(
        min_length=1,
        description="Categoría temática utilizada para filtrado.",
    )

    namespace: str = Field(
        min_length=1,
        description="Namespace de Pinecone donde se almacena el vector.",
    )

    text: str = Field(
        min_length=1,
        description="Contenido original asociado al vector.",
    )

    @field_validator("source", "category", "namespace")
    @classmethod
    def normalize_strings(cls, value: str) -> str:
        return value.strip()


class RetrievedDocument(BaseModel):
    document_id: str = Field(
        min_length=1,
        description="Identificador único del documento recuperado.",
    )

    content: str = Field(
        min_length=1,
        description="Fragmento de texto recuperado.",
    )

    source: str = Field(
        min_length=1,
        description="Documento fuente del fragmento.",
    )

    category: str = Field(
        min_length=1,
        description="Categoría asociada al documento.",
    )

    score: float | None = Field(default=None,
        ge=0,
        description="Puntaje producido por el recuperador.",
    )

    retrieval_type: Literal[
        "vector",
        "bm25",
        "hybrid",
    ] = Field(
        description="Tipo de recuperación utilizada.",
    )


class EvaluationResult(BaseModel):
    question: str = Field(
        min_length=1,
        description="Pregunta evaluada.",
    )

    expected_document_id: str = Field(
        min_length=1,
        description="Documento esperado según el golden set.",
    )

    retrieved_document_ids: list[str] = Field(
        description="IDs de los documentos recuperados en el Top-K.",
    )

    recall_at_5: float = Field(
        ge=0,
        le=1,
        description="Recall@5 de la consulta.",
    )

    precision_at_5: float = Field(
        ge=0,
        le=1,
        description="Precision@5 de la consulta.",
    )