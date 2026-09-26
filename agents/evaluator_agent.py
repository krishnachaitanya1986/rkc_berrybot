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
    strengths: List[str] = Field(max_length=3)
    missing_points: List[str] = Field(max_length=5)
    feedback: str
    recommended_level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ]


def evaluator_agent(state):
    llm = get_llm(0).bind(
        response_format={"type": "json_object"}
    )

    prompt = f"""
Act as a strict but fair senior technical interviewer.

Technology: {state["current_technology"]}
Current level: {state["current_level"]}
Question type: {state["question_type"]}

Question:
{state["current_question"]}

Candidate answer:
{state["current_answer"]}

Evaluate the answer using these categories:
- technical_correctness: 0 to 40
- completeness: 0 to 20
- practical_understanding: 0 to 15
- problem_solving: 0 to 15
- communication: 0 to 10

For a coding answer, consider correctness, edge cases, complexity,
readability, and whether the solution would work.

Set score to the sum of the five category scores, out of 100.
Set recommended_level to the appropriate difficulty for the NEXT
question based on this answer.

Return ONLY one valid JSON object with exactly these fields:
{{
  "score": 0,
  "technical_correctness": 0,
  "completeness": 0,
  "practical_understanding": 0,
  "problem_solving": 0,
  "communication": 0,
  "strengths": [],
  "missing_points": [],
  "feedback": "Brief, specific feedback",
  "recommended_level": "beginner"
}}

Use numeric values for scores. recommended_level must be exactly
"beginner", "intermediate", or "advanced".
Include at most 3 distinct strengths and 5 distinct missing_points.
Keep each list item short, with no repeated points.
Keep feedback under 100 words.
Do not include Markdown or text outside the JSON object.
"""

    response = llm.invoke(prompt)
    result = Evaluation.model_validate_json(response.content)

    # Make the overall score consistent with the category scores,
    # even if the model adds them incorrectly.
    final_score = round(
        result.technical_correctness
        + result.completeness
        + result.practical_understanding
        + result.problem_solving
        + result.communication,
        2,
    )

    tech = state["current_technology"]

    history = list(state["questions"])
    history.append({
        "technology": tech,
        "level": state["current_level"],
        "type": state["question_type"],
        "question": state["current_question"],
        "answer": state["current_answer"],
        "score": final_score,
        "strengths": result.strengths,
        "missing_points": result.missing_points,
        "feedback": result.feedback,
    })

    scores = list(state["scores"])
    scores.append(final_score)

    tech_scores = {
        key: list(values)
        for key, values in state["technology_scores"].items()
    }
    tech_scores.setdefault(tech, []).append(final_score)

    return {
        "current_score": final_score,
        "feedback": result.feedback,
        "questions": history,
        "scores": scores,
        "technology_scores": tech_scores,
        "current_level": result.recommended_level,
        "question_number": state["question_number"] + 1,
    }