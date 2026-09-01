from app.state import ResearchState
from app.config import llm


def planner_node(state: ResearchState):
    print("[PLANNER] Starting...")
    query = state["user_query"]

    prompt = f"""
You are a research planning agent.

The user wants a well-researched, factual report on:

{query}

Break this topic into 4-6 specific research questions
that need to be answered before writing the final report.

Return only the research questions, one per line.
"""
    print("[PLANNER] Calling LLM...")
    response = llm.invoke(prompt)
    print("[PLANNER] LLM finished.")

    research_plan = [
        line.strip("- ")
        for line in response.content.split("\n")
        if line.strip()
    ]

    return {
        "research_plan": research_plan
    }