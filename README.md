# LangGraph Multi-Agent Interview Platform

A VS Code-ready interview preparation and screening application.

## Features

- Software track: Core Java, Spring Boot, Microservices, Kafka, SQL, Angular, React,Azure,Azure DevOps,AWS,GCP,Docker,Kubernetes
- AI track: Generative AI, Machine Learning, Agentic AI
- Beginner / Intermediate / Advanced adaptive levels
- Text interview mode
- Coding-question evaluation
- Voice input using browser microphone (Streamlit)
- Per-answer score and feedback
- Adaptive difficulty
- Technology-wise final report
- LangGraph state machine

## Architecture

```text
UI (Streamlit)
      |
      v
LangGraph Interview Graph
      |
      +--> Technology Selector
      |
      +--> Question Agent
      |
      +--> Candidate Answer
      |
      +--> Evaluation Agent
      |
      +--> Adaptive Level Agent
      |
      +--> Next Question / Finish
                         |
                         v
                    Final Report
```

## 1. Open in VS Code

Unzip this project and open the folder:

```bash
code langgraph-interview-platform
```

## 2. Create virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

## 3. Install

```bash
pip install -r requirements.txt
```

## 4. Configure OpenAI

Copy:

```bash
cp .env.example .env
```

Then set:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
```

## 5. Run

```bash
streamlit run app.py
```

Open the URL Streamlit prints, normally localhost:8501.

## Voice mode

Choose Voice mode. The browser microphone records the candidate answer. The audio is transcribed before evaluation.

## Important production note

The coding evaluator in this starter uses LLM evaluation. For real hiring/screening, execute code in an isolated sandbox with test cases and combine deterministic test results with the model evaluation.
# rkc_berrybot
