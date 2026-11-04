from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

from app.state import ResearchState
from app.planner import planner_node
from app.researcher import researcher_node
from app.writer import writer_node
from app.human_review import human_review_node
from app.routers import human_review_router
from app.followup import follow_up_node


builder = StateGraph(ResearchState)

builder.add_node("planner", planner_node)
builder.add_node("researcher", researcher_node)
builder.add_node("writer", writer_node)
builder.add_node("human_review", human_review_node)
builder.add_node("follow_up", follow_up_node)


def start_route(state: ResearchState):

    if state.get("follow_up_question"):
        return "follow_up"

    return "planner"


builder.add_conditional_edges(
    START,
    start_route,
    {
        "planner": "planner",
        "follow_up": "follow_up"
    }
)


builder.add_edge("planner", "researcher")
builder.add_edge("researcher", "writer")
builder.add_edge("writer","human_review")


builder.add_conditional_edges(
    "human_review",
    human_review_router,
    {
        "end": END,
        "researcher": "researcher"
    }
)


builder.add_edge("follow_up", END)


checkpointer = InMemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)