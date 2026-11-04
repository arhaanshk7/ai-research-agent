from app.state import ResearchState
from app.config import llm, content_to_text
from langgraph.config import get_stream_writer


def follow_up_node(state: ResearchState):

    print("\n[FOLLOW-UP] Starting...")

    stream_writer = get_stream_writer()

    question = state["follow_up_question"]
    report = state["draft_report"]

    prompt = f"""
You are an AI research assistant.

Answer the user's follow-up question using the research report below.

RESEARCH REPORT:
{report}

FOLLOW-UP QUESTION:
{question}

REQUIREMENTS:
- Answer clearly and accurately.
- Use only information supported by the research report.
- Do not invent facts.
- If the report does not contain enough information to answer, say so.
- Give a useful but reasonably sized answer.
- Use Markdown when helpful.

Answer the follow-up question now.
"""

    print("[FOLLOW-UP] Calling LLM...\n")

    full_response = ""

    for chunk in llm.stream(prompt):

        text = content_to_text(chunk.content)

        if text:

            print(text, end="", flush=True)

            stream_writer({
                "type": "followup_chunk",
                "content": text
            })

            full_response += text

    print("\n\n[FOLLOW-UP] Completed.")

    return {
        "follow_up_answer": full_response
    }