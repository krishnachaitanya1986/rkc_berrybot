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

    return {
        "overall_score": avg,
        "final_level": level,
    }


def report_agent(state):
    llm = get_llm(0.2)

    candidate_name = state.get("candidate_name") or "Not Provided"
    interviewer_name = state.get("interviewer_name") or "Not Provided"
    interview_date = state.get("interview_date") or "Not Provided"

    breakdown = {
        tech: round(sum(values) / len(values), 2)
        for tech, values in state["technology_scores"].items()
        if values
    }

    prompt = f"""
Create a concise, professional technical interview assessment.

Interview information:
- Candidate: {candidate_name}
- Interviewer: {interviewer_name}
- Interview date: {interview_date}
- Track: {state["track"]}
- Overall score: {state["overall_score"]}/100
- Overall assessed level: {state["final_level"]}
- Technology scores: {breakdown}
- Interview history: {state["questions"]}

Write only the assessment body with these sections:
1. Executive summary
2. Technology-wise assessment
3. Strong areas
4. Improvement areas
5. Coding/problem-solving assessment
6. Communication assessment
7. A practical 2-week improvement plan

Do not add an "Interview Information" section or repeat the candidate,
interviewer, or date as a header. The application adds that header itself.
Do not inflate performance. Base every conclusion on the interview evidence.
"""

    result = llm.invoke(prompt)

    # Build factual metadata from state instead of relying on model output.
    report_header = f"""### Interview Information

**Candidate:** {candidate_name}  
**Interviewer:** {interviewer_name}  
**Interview Date:** {interview_date}  
**Track:** {state["track"]}  
**Overall Score:** {state["overall_score"]}/100  
**Assessed Level:** {state["final_level"]}

---

"""

    return {
        "final_report": report_header + result.content
    }