from typing import TypedDict, List, Dict, Any

class InterviewState(TypedDict):
    candidate_name: str
    interviewer_name: str
    interview_date: str
    track: str
    technologies: List[str]
    mode: str
    current_technology: str
    current_level: str
    question_number: int
    max_questions: int
    current_question: str
    question_type: str
    current_answer: str
    current_score: float
    feedback: str
    questions: List[Dict[str, Any]]
    scores: List[float]
    technology_scores: Dict[str, List[float]]
    overall_score: float
    final_level: str
    final_report: str
   
