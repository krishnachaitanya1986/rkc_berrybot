import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_llm(temperature: float = 0.2):
    """
    get_llm()  -> default temperature
    get_llm(0) -> temperature 0, as used by evaluator_agent.py
    """
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    return ChatGroq(
        model=os.getenv("GROQ_LLM_MODEL", "openai/gpt-oss-20b"),
        temperature=temperature,
        max_tokens=1500,
    )