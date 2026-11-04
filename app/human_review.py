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
        "human_feedback": decision.get("feedback", ""),
        # Fresh revision cycle: reset quality-check bookkeeping
        "revision_attempts": 0,
        "quality_missing": []
    }