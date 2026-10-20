
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def crear_modelo():
    """Configura el modelo de OpenAI para los agentes."""

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError(
            "Falta OPENAI_API_KEY en el archivo .env"
        )

    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        temperature=0,
        api_key=api_key,
    )
