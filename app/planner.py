import json

from langgraph.config import get_stream_writer

from app.state import ResearchState
from app.config import llm, content_to_text


def planner_node(state: ResearchState):
    print("[PLANNER] Starting...")

    prompt = f"""
You are a research planning agent.

The user wants a well-researched, factual report on:
{state["user_query"]}

Return ONLY JSON in this format:
{{
    "research_questions": [
        "specific question 1",
        "specific question 2",
        "specific question 3",
        "specific question 4"
    ],
    "title": "Report title",
    "subtitle": "Short description",
    "category": "Technical Research",
    "sections": ["Section 1", "Section 2", "Section 3"]
}}

Create 4-6 research questions and 3-5 report sections.
"""

    print("[PLANNER] Calling LLM...")
    response = llm.invoke(prompt)
    print("[PLANNER] LLM finished.")

    text = content_to_text(response.content).strip()
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)

    meta = {
        "title": data.get("title") or state["user_query"],
        "subtitle": data.get("subtitle", ""),
        "category": data.get("category", "Technical Research"),
    }

    sections = data.get("sections", [])
    outline = "\n".join(f"- {section}" for section in sections)

    stream_writer = get_stream_writer()
    stream_writer({"type": "report_meta", "meta": meta})

    return {
        "research_plan": data.get("research_questions") or [state["user_query"]],
        "report_outline": outline,
        "report_meta": meta,
    }
