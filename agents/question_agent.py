from pydantic import BaseModel, Field
from typing import Literal
from services.llm_service import get_llm

class QuestionOutput(BaseModel):
    question: str
    question_type: Literal["theory", "scenario", "coding"]

def question_agent(state):
    llm = get_llm().with_structured_output(QuestionOutput)

    tech = state["current_technology"]
    level = state["current_level"]
    mode = state["mode"]

    coding_allowed = mode == "text" and tech in [
        "Core Java", "Spring Boot", "Kafka", "SQL",
        "Angular", "React", "Machine Learning",
        "Generative AI", "Agentic AI","Azure","Azure DevOps","AWS","GCP","Docker","Kubernetes"
    ]

    prompt = f"""
You are a senior technical interviewer.

Technology: {tech}
Candidate level: {level}
Interview mode: {mode}
Question number: {state['question_number'] + 1}

Generate exactly one question.

Difficulty:
- beginner: fundamentals and straightforward implementation
- intermediate: practical implementation, debugging and production scenarios
- advanced: internals, architecture, performance, scalability and trade-offs

{"Coding questions are allowed and encouraged when appropriate." if coding_allowed else "Ask a spoken-friendly theory or scenario question. Do not ask the candidate to write code."}

Do not reveal the answer. Avoid repeating previous questions:
{[q.get("question") for q in state["questions"]]}
"""

    result = llm.invoke(prompt)
    return {
        "current_question": result.question,
        "question_type": result.question_type,
        "current_answer": "",
        "feedback": ""
    }
