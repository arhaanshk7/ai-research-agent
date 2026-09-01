from langgraph.types import interrupt
from app.state import ResearchState


def human_review_node(state: ResearchState):

    print("\n[HUMAN REVIEW] Waiting for review...")

    decision = interrupt({
        "type": "human_review",
        "report": state["draft_report"],
        "message": "Approve this research report?"
    })

    return {
        "human_approved": decision["approved"],
        "human_feedback": decision.get("feedback", "")
    }


def human_review_router(state: ResearchState):

    if state["human_approved"]:
        return "end"

    if state.get("retry_count", 0) >= 4:
        return "end"

    return "researcher"