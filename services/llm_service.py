import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv()


def get_llm(temperature: float = 0.3):
    """
    Returns local Ollama LLM.

    Examples:
        get_llm()      -> temperature 0.3
        get_llm(0)     -> deterministic
        get_llm(0.4)   -> slightly creative
    """

    model = os.getenv("OLLAMA_MODEL", "qwen2:7b")
    base_url = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature
    )