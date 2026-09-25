from typing import Literal

from pydantic import BaseModel, Field
from services.llm_service import get_llm


class QuestionOutput(BaseModel):
    question: str = Field(description="One interview question only")
    question_type: Literal["theory", "scenario", "coding"]


def question_agent(state):
    tech = state["current_technology"]
    level = state["current_level"]
    mode = state["mode"]

    coding_allowed = mode == "text" and tech in [
        "Core Java",
        "Spring Boot",
        "Kafka",
        "SQL",
        "Angular",
        "React",
        "Machine Learning",
        "Generative AI",
        "Agentic AI",
        "Azure",
        "Azure DevOps",
        "AWS",
        "GCP",
        "Docker",
        "Kubernetes",
    ]

    previous_questions = [
        q.get("question")
        for q in state["questions"]
        if q.get("question")
    ]

    question_instruction = (
        "Coding questions are allowed when appropriate."
        if coding_allowed
        else (
            "Ask a spoken-friendly theory or scenario question. "
            "Do not ask the candidate to write code."
        )
    )

    prompt = f"""
You are a senior technical interviewer.

Technology: {tech}
Candidate level: {level}
Interview mode: {mode}
Question number: {state["question_number"] + 1}

Generate exactly one question.

Difficulty:
- beginner: fundamentals and straightforward implementation
- intermediate: practical implementation, debugging and production scenarios
- advanced: internals, architecture, performance, scalability and trade-offs

{question_instruction}

Do not reveal the answer.
Avoid repeating these previous questions:
{previous_questions}

Return ONLY a valid JSON object with exactly these fields:
{{
  "question": "The complete question text",
  "question_type": "theory"
}}

Set question_type to exactly one of: "theory", "scenario", "coding".
If coding questions are not allowed, use only "theory" or "scenario".
Do not include Markdown fences or text outside the JSON object.
"""

    # Groq JSON mode returns JSON text without requiring a tool call.
    llm = get_llm().bind(
        response_format={"type": "json_object"}
    )

    response = llm.invoke(prompt)

    # Validate the JSON and convert it into the expected Pydantic object.
    result = QuestionOutput.model_validate_json(response.content)

    if not coding_allowed and result.question_type == "coding":
        raise ValueError(
            "The model generated a coding question in spoken interview mode."
        )

    return {
        "current_question": result.question,
        "question_type": result.question_type,
        "current_answer": "",
        "feedback": "",
    }