from langgraph.graph import StateGraph, START, END
from state import InterviewState
from agents.question_agent import question_agent
from agents.evaluator_agent import evaluator_agent
from agents.report_agent import scoring_agent, report_agent

def technology_selector(state):
    technologies = state["technologies"]
    index = state["question_number"] % len(technologies)
    return {"current_technology": technologies[index]}

def build_question_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("technology_selector", technology_selector)
    builder.add_node("question_agent", question_agent)
    builder.add_edge(START, "technology_selector")
    builder.add_edge("technology_selector", "question_agent")
    builder.add_edge("question_agent", END)
    return builder.compile()

def build_evaluation_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("evaluator_agent", evaluator_agent)
    builder.add_edge(START, "evaluator_agent")
    builder.add_edge("evaluator_agent", END)
    return builder.compile()

def build_report_graph():
    builder = StateGraph(InterviewState)
    builder.add_node("scoring_agent", scoring_agent)
    builder.add_node("report_agent", report_agent)
    builder.add_edge(START, "scoring_agent")
    builder.add_edge("scoring_agent", "report_agent")
    builder.add_edge("report_agent", END)
    return builder.compile()

question_graph = build_question_graph()
evaluation_graph = build_evaluation_graph()
report_graph = build_report_graph()
