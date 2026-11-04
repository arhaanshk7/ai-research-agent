from app.state import ResearchState
from fastapi import FastAPI


def human_review_router(state: ResearchState):

    if state["human_approved"]:
        return "end"

    if state.get("retry_count", 0) >= 3:
        return "end"

    return "researcher"
