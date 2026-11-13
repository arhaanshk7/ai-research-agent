from app.state import ResearchState

MAX_RETRIES = 2


def human_review_router(state: ResearchState):

    if state["human_approved"]:
        return "end"

    # The first research run counts as 1, so allow MAX_RETRIES extra runs.
    if state.get("retry_count", 0) >= MAX_RETRIES + 1:
        return "end"

    return "researcher"
