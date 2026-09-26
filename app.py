from datetime import date

import streamlit as st

from config import AI_TECHNOLOGIES, ALL_TECHNOLOGIES
from interview_graph import question_graph, evaluation_graph, report_graph
from services.voice_service import transcribe_audio
from services.report_pdf import build_report_pdf

st.set_page_config(
    page_title="AI Interview Agent",
    page_icon="🎯",
    layout="wide",
)


def new_state(
    name,
    interviewer_name,
    interview_date,
    track,
    technologies,
    mode,
    level,
    max_questions,
):
    return {
        "candidate_name": name.strip() or "Candidate",
        "interviewer_name": interviewer_name.strip() or "Not Provided",
        "interview_date": interview_date.isoformat(),
        "track": track,
        "technologies": technologies,
        "mode": mode.lower(),
        "current_technology": "",
        "current_level": level.lower(),
        "question_number": 0,
        "max_questions": max_questions,
        "current_question": "",
        "question_type": "theory",
        "current_answer": "",
        "current_score": 0.0,
        "feedback": "",
        "questions": [],
        "scores": [],
        "technology_scores": {},
        "overall_score": 0.0,
        "final_level": "",
        "final_report": "",
    }


def invoke_preserving_details(graph, interview):
    """Keep interview metadata even if a graph returns only its declared fields."""
    details = {
        "candidate_name": interview.get("candidate_name", "Candidate"),
        "interviewer_name": interview.get(
            "interviewer_name", "Not Provided"
        ),
        "interview_date": interview.get(
            "interview_date", "Not Provided"
        ),
    }

    result = graph.invoke(interview)
    return {**result, **details}


def generate_question():
    st.session_state.interview = invoke_preserving_details(
        question_graph,
        st.session_state.interview,
    )


def finish_interview():
    st.session_state.interview = invoke_preserving_details(
        report_graph,
        st.session_state.interview,
    )
    st.session_state.finished = True


st.title("🎯 Multi-Agent Technical Interview Platform")
st.caption(
    "LangGraph • Adaptive Interview • Text/Coding • Voice • Final Assessment"
)

if "interview" not in st.session_state:
    st.session_state.interview = None

if "finished" not in st.session_state:
    st.session_state.finished = False

if "interview_id" not in st.session_state:
    st.session_state.interview_id = 0


with st.sidebar:
    st.header("Interview Setup")

    name = st.text_input("Candidate name", value="Candidate")
    interviewer_name = st.text_input(
        "Interviewer name",
        placeholder="Enter interviewer name",
    )
    interview_date = st.date_input(
        "Interview date",
        value=date.today(),
    )

    track = st.selectbox(
        "Track",
        [
            "Java Full Stack",
            "Backend",
            "Frontend",
            "Cloud",
            "AI Engineer",
            "Custom",
        ],
    )

    defaults = {
        "Java Full Stack": [
            "Core Java",
            "Spring Boot",
            "Microservices",
            "Kafka",
            "SQL",
            "Angular",
        ],
        "Backend": [
            "Core Java",
            "Spring Boot",
            "Microservices",
            "Kafka",
            "SQL",
        ],
        "Frontend": ["Angular", "React"],
        "Cloud": [
            "Azure",
            "Azure DevOps",
            "AWS",
            "GCP",
            "Docker",
            "Kubernetes",
        ],
        "AI Engineer": AI_TECHNOLOGIES,
        "Custom": ALL_TECHNOLOGIES,
    }

    technologies = st.multiselect(
        "Technologies",
        ALL_TECHNOLOGIES,
        default=defaults[track],
    )

    mode = st.radio("Answer mode", ["Text", "Voice"])
    level = st.selectbox(
        "Starting level",
        ["Beginner", "Intermediate", "Advanced"],
    )
    max_questions = st.slider(
        "Number of questions",
        3,
        30,
        10,
    )

    if st.button(
        "Start / Restart Interview",
        type="primary",
        use_container_width=True,
    ):
        if not technologies:
            st.error("Select at least one technology.")
        else:
            st.session_state.interview_id += 1
            st.session_state.interview = new_state(
                name,
                interviewer_name,
                interview_date,
                track,
                technologies,
                mode,
                level,
                max_questions,
            )
            st.session_state.finished = False
            st.session_state.pop("last_feedback", None)

            generate_question()
            st.rerun()


state = st.session_state.interview

if not state:
    st.info(
        "Configure the interview in the left sidebar "
        "and click Start / Restart Interview."
    )
    st.stop()


if st.session_state.finished:
    st.success("Interview completed")

    st.subheader("Interview Information")
    st.write(
        f"**Candidate:** "
        f"{state.get('candidate_name') or 'Not Provided'}"
    )
    st.write(
        f"**Interviewer:** "
        f"{state.get('interviewer_name') or 'Not Provided'}"
    )
    st.write(
        f"**Interview Date:** "
        f"{state.get('interview_date') or 'Not Provided'}"
    )

    c1, c2 = st.columns(2)
    c1.metric(
        "Overall Score",
        f"{state['overall_score']}/100",
    )
    c2.metric(
        "Assessed Level",
        state["final_level"],
    )

    st.subheader("Technology Breakdown")
    for tech, values in state["technology_scores"].items():
        if not values:
            continue

        avg = sum(values) / len(values)
        st.write(f"**{tech}: {avg:.1f}/100**")
        st.progress(min(max(avg / 100, 0.0), 1.0))

    st.subheader("Final Interview Report")
    st.markdown(state["final_report"])
    
    safe_name = "".join(
    char if char.isalnum() or char in ("-", "_") else "_"
    for char in state.get("candidate_name", "Candidate")
    )
    report_date = state.get("interview_date", "undated")

    pdf_bytes = build_report_pdf(state["final_report"])

    st.download_button(
        label="⬇️ Download Interview Report (PDF)",
        data=pdf_bytes,
        file_name=f"interview_report_{safe_name}_{report_date}.pdf",
        mime="application/pdf",
        key="download_interview_pdf",
        use_container_width=True,
    )

    with st.expander("Full Q&A history"):
        for i, item in enumerate(state["questions"], 1):
            st.markdown(
                f"### Q{i} — "
                f"{item['technology']} ({item['level']})"
            )
            st.write(item["question"])
            st.code(item["answer"])
            st.write(
                f"Score: **{item['score']}/100**"
            )
            st.write(item["feedback"])

    st.stop()


progress = state["question_number"] / state["max_questions"]
st.progress(progress)

st.write(
    f"Question **{state['question_number'] + 1} / "
    f"{state['max_questions']}** "
    f"• **{state['current_technology']}** "
    f"• Level: **{state['current_level'].title()}** "
    f"• Type: **{state['question_type'].title()}**"
)

st.subheader("Interview Question")
st.info(state["current_question"])


answer_key = (
    f"answer_{st.session_state.interview_id}_"
    f"{state['question_number']}"
)

if state["mode"] == "text":
    answer = st.text_area(
        "Your answer / code",
        key=answer_key,
        height=260,
        placeholder=(
            "Type your explanation or paste your code here..."
        ),
    )

else:
    st.write("Record your spoken answer below.")

    audio = st.audio_input(
        "Record answer",
        key=(
            f"audio_{st.session_state.interview_id}_"
            f"{state['question_number']}"
        ),
    )

    if audio and st.button("Transcribe Voice"):
        with st.spinner("Transcribing..."):
            try:
                transcript = transcribe_audio(
                    audio.getvalue()
                )
                st.session_state[answer_key] = transcript
            except Exception as exc:
                st.error(
                    f"Transcription failed: {exc}"
                )

    answer = st.text_area(
        "Transcript (you can correct transcription errors "
        "before submitting)",
        key=answer_key,
        height=220,
    )


if st.button("Submit Answer", type="primary"):
    if not answer.strip():
        st.warning("Please provide an answer.")
    else:
        state["current_answer"] = answer.strip()

        with st.spinner("Evaluating answer..."):
            state = invoke_preserving_details(
                evaluation_graph,
                state,
            )
            st.session_state.interview = state

        if state["question_number"] >= state["max_questions"]:
            with st.spinner(
                "Generating final assessment..."
            ):
                finish_interview()
            st.rerun()

        else:
            st.session_state.last_feedback = {
                "score": state["current_score"],
                "feedback": state["feedback"],
                "next_level": state["current_level"],
            }

            with st.spinner(
                "Preparing next adaptive question..."
            ):
                generate_question()

            st.rerun()


if (
    "last_feedback" in st.session_state
    and state["question_number"] > 0
):
    fb = st.session_state.last_feedback

    with st.expander(
        "Previous answer feedback",
        expanded=True,
    ):
        st.metric(
            "Score",
            f"{fb['score']}/100",
        )
        st.write(fb["feedback"])
        st.caption(
            f"Next difficulty: "
            f"{fb['next_level'].title()}"
        )