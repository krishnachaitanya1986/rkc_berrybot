from services.llm_service import get_llm

def scoring_agent(state):
    scores = state["scores"]
    avg = round(sum(scores) / len(scores), 2) if scores else 0.0

    if avg >= 80:
        level = "Advanced"
    elif avg >= 55:
        level = "Intermediate"
    else:
        level = "Beginner"

    return {"overall_score": avg, "final_level": level}

def report_agent(state):
    llm = get_llm(0.2)

    breakdown = {
        tech: round(sum(values) / len(values), 2)
        for tech, values in state["technology_scores"].items()
        if values
    }

    prompt = f"""
Create a concise professional technical interview report.

Candidate: {state['candidate_name']}
Track: {state['track']}
Overall score: {state['overall_score']}/100
Overall assessed level: {state['final_level']}
Technology scores: {breakdown}
Interview history: {state['questions']}

Include:
1. Executive summary
2. Technology-wise assessment
3. Strong areas
4. Improvement areas
5. Coding/problem-solving assessment
6. Communication assessment
7. A practical 2-week improvement plan

Do not inflate performance. Base every conclusion on the interview evidence.
"""

    result = llm.invoke(prompt)
    return {"final_report": result.content}
