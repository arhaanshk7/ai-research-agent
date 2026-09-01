
from app.state import ResearchState
from app.config import llm
from langgraph.config import get_stream_writer


def writer_node(state: ResearchState):

    print("\n[WRITER] Starting...")

    # Get LangGraph stream writer
    stream_writer = get_stream_writer()

    # Keep only useful research fields
    research = [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "content": r.get("content")
        }
        for r in state["research_results"]
    ]

    sources = state["sources"]

    prompt = f"""
You are a professional research report writer.

Write a high-quality research report based ONLY on the research provided below.

RESEARCH:
{research}

REPORT REQUIREMENTS:

1. Write a detailed but reasonably sized report.
2. Target approximately 800–1000 words.
3. Focus on the most important and useful information.
4. Do not repeat the same information.
5. Use clear Markdown headings and subheadings.
6. Use bullet points when useful.
7. Only use information contained in the research.
8. Keep the report professional, factual, and easy to understand.

Suggested structure:

• Title

• Executive Summary

• Key Findings

• Important Evidence

• Analysis

• Implications

• Conclusion

Write the report now.
"""

    print("[WRITER] Calling LLM...\n")

    full_response = ""

    # --------------------------------
    # Stream LLM report
    # --------------------------------

    for chunk in llm.stream(prompt):

        if chunk.content:

            # Show chunk in backend terminal
            print(
                chunk.content,
                end="",
                flush=True
            )

            # Send chunk to frontend through LangGraph
            stream_writer({
                "type": "report_chunk",
                "content": chunk.content
            })

            # Save complete response
            full_response += chunk.content


    # --------------------------------
    # Add real sources
    # --------------------------------

    sources_text = "\n\n## Sources\n\n"

    for source in sources:

        title = source.get("title")
        url = source.get("url")

        if title and url:

            source_line = f"- [{title}]({url})\n"

            sources_text += source_line

            # Send source to frontend
            stream_writer({
                "type": "source",
                "content": source_line
            })


    # --------------------------------
    # Create complete report
    # --------------------------------

    final_report = full_response + sources_text

    print("\n\n[WRITER] LLM response completed.")

    return {
        "draft_report": final_report
    }

