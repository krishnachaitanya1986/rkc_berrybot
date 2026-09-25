from typing import List, Literal
from pydantic import BaseModel, Field
from services.llm_service import get_llm

class Evaluation(BaseModel):
    score: float = Field(ge=0, le=100)
    technical_correctness: float = Field(ge=0, le=40)
    completeness: float = Field(ge=0, le=20)
    practical_understanding: float = Field(ge=0, le=15)
    problem_solving: float = Field(ge=0, le=15)
    communication: float = Field(ge=0, le=10)
    strengths: List[str]
    missing_points: List[str]
    feedback: str
    recommended_level: Literal["beginner", "intermediate", "advanced"]

def evaluator_agent(state):
    llm = get_llm(0).with_structured_output(Evaluation)

    prompt = f"""
Act as a strict but fair senior interviewer.

Technology: {state['current_technology']}
Current level: {state['current_level']}
Question type: {state['question_type']}

Question:
{state['current_question']}

Candidate answer:
{state['current_answer']}

Evaluate the answer on:
- technical correctness: 0-40
- completeness: 0-20
- practical understanding: 0-15
- problem solving: 0-15
- communication: 0-10

The total score must represent the overall quality out of 100.

For coding answers also inspect correctness, edge cases, complexity,
readability and whether the solution would work.

recommended_level should represent the difficulty appropriate for the
candidate's NEXT question based on this answer.
"""

    result = llm.invoke(prompt)
    tech = state["current_technology"]

    history = list(state["questions"])
    history.append({
        "technology": tech,
        "level": state["current_level"],
        "type": state["question_type"],
        "question": state["current_question"],
        "answer": state["current_answer"],
        "score": result.score,
        "strengths": result.strengths,
        "missing_points": result.missing_points,
        "feedback": result.feedback,
    })

    scores = list(state["scores"])
    scores.append(result.score)

    tech_scores = {k: list(v) for k, v in state["technology_scores"].items()}
    tech_scores.setdefault(tech, []).append(result.score)

    return {
        "current_score": result.score,
        "feedback": result.feedback,
        "questions": history,
        "scores": scores,
        "technology_scores": tech_scores,
        "current_level": result.recommended_level,
        "question_number": state["question_number"] + 1,
    }
