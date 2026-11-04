
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import json
from langgraph.types import Command


from app.graph import graph


app = FastAPI()


# -------------------------
# CORS
# -------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# Request Models
# -------------------------

class ResearchRequest(BaseModel):
    topic: str


class ReviewRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: str = ""


class FollowUpRequest(BaseModel):
    thread_id: str
    question: str


# -------------------------
# Research Route
# -------------------------




@app.post("/research")
def research(request: ResearchRequest):

    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "user_query": request.topic,
        "research_plan": [],
        "research_results": [],
        "sources": [],
        "draft_report": "",
        "report_outline": "",
        "report_meta": {},
        "human_approved": False,
        "human_feedback": "",
        "quality_passed": True,
        "quality_missing": [],
        "revision_attempts": 0,
        "follow_up_question": "",
        "follow_up_answer": "",
        "retry_count": 0
    }

    def generate():

        # 1. Send thread ID
        yield json.dumps({
            "type": "thread_id",
            "thread_id": thread_id
        }) + "\n"


        # 2. Run graph
        for chunk in graph.stream(
            initial_state,
            config=config,
            stream_mode="custom"
        ):

            # 3. Forward report chunks and report metadata
            if chunk.get("type") in ["report_chunk", "report_meta"]:

                yield json.dumps(chunk) + "\n"



        # graph.stream() has finished.
        # Therefore Writer has completely finished.

        final_state = graph.get_state(config).values

        yield json.dumps({
            "type": "review_ready",
            "report": final_state.get("draft_report", ""),
            "meta": final_state.get("report_meta", {}),
        }) + "\n"


    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )
# -------------------------
# Human Review Route
# -------------------------

@app.post("/review")
def review(request: ReviewRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    # Resume the paused graph
    result = graph.invoke(
        Command(
            resume={
                "approved": request.approved,
                "feedback": request.feedback
            }
        ),
        config=config
    )

    # Approved
    if request.approved:

        return {
            "thread_id": request.thread_id,
            "status": "approved",
            "message": "Research approved.",
        }

    # Changes requested
    return {
        "thread_id": request.thread_id,
        "status": "revised",
        "report": result.get("draft_report", ""),
        "meta": result.get("report_meta", {}),
    }

# -------------------------
# Follow-up Route
# -------------------------

@app.post("/follow-up")
def follow_up(request: FollowUpRequest):

    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    def generate():

        for chunk in graph.stream(
            {
                "follow_up_question": request.question
            },
            config=config,
            stream_mode="custom"
        ):

            print("[FOLLOW-UP STREAM]:", chunk)

            if chunk.get("type") == "followup_chunk":

                yield json.dumps(chunk) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson"
    )
