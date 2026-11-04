from langgraph.config import get_stream_writer

from app.state import ResearchState
from app.config import llm, content_to_text
from app.citations import build_numbered_sources, validate_report


EVIDENCE_LIMIT = 2000


def build_evidence(state: ResearchState, sources: list[dict]) -> list[str]:
    """Attach each research result to its citation number."""

    source_by_url = {source["url"]: source for source in sources}

    evidence = []
    used = set()

    for result in state.get("research_results", []):

        url = str(result.get("url") or "").strip()
        source = source_by_url.get(url)

        if source is None or url in used:
            continue

        used.add(url)

        content = str(result.get("content") or "").strip()[:EVIDENCE_LIMIT]

        evidence.append(
            f"[{source['n']}] {source['title']}\n"
            f"URL: {url}\n"
            f"{content}"
        )

    return evidence


def writer_node(state: ResearchState):

    print("\n[WRITER] Starting...")

    stream_writer = get_stream_writer()

    query = state["user_query"]
    meta = state.get("report_meta") or {}
    title = meta.get("title") or query
    subtitle = meta.get("subtitle") or ""
    outline = state.get("report_outline", "")

    sources = build_numbered_sources(state.get("research_results", []))
    evidence = build_evidence(state, sources)

    plan = "\n".join(
        f"- {q}" for q in state.get("research_plan", []) if q and q.strip()
    )

    feedback = str(state.get("human_feedback") or "").strip()
    missing = [m for m in state.get("quality_missing", []) if str(m).strip()]

    # Revision prompt: only added when the reviewer rejected the report
    revision_block = ""

    if feedback:
        print("[WRITER] Addressing reviewer feedback.")

        revision_block = f"""
REVIEWER FEEDBACK (this revision MUST address every point):
{feedback}
"""

        if missing:
            revision_block += "\nSTILL NOT ADDRESSED (a quality check failed on the previous revision):\n"
            revision_block += "\n".join(f"- {m}" for m in missing)
            revision_block += "\n"

        revision_block += """
REVISION RULES:
- Address every point of the reviewer feedback exactly as the reviewer asked.
- Remove or correct any statistic or claim the reviewer flagged as
  unsupported. Never invent statistics: every number must appear in the
  VERIFIED EVIDENCE below and carry its citation.
- Do not repeat content the reviewer told you to remove.
"""

    sources_block = "\n\n".join(evidence) if evidence else "No evidence collected."

    prompt = f"""
You are an expert research report writer.

Write a complete, evidence-grounded research report in Markdown.

REPORT TITLE: {title}
SUBTITLE: {subtitle}
TOPIC: {query}

RESEARCH QUESTIONS:
{plan}

REPORT OUTLINE (topic-specific sections to include, in order):
{outline or "- (no extra sections)"}
{revision_block}
VERIFIED EVIDENCE (cite only these sources, using their bracket numbers):
{sources_block}

STRUCTURE (exactly this order):

1. First line: `# {title}` then one line with the subtitle in italics: `*{subtitle}*`
2. `## Executive Summary` — 3-5 sentences covering the main findings, the overall
   conclusion, and the most important uncertainties.
3. `## Key Findings` — 3-5 findings. Each finding starts with
   `### Finding N: <short claim>`, followed by 1-2 paragraphs that explain the
   finding and attach an inline citation to the relevant claim, e.g. [1].
4. `## Evidence and Analysis` — in-depth analysis: statistics, source
   comparisons, trends, and implications. When the evidence supports it, include
   a Markdown comparison table introduced by a bold caption such as
   **Evidence at a glance**.
5. Any topic-specific sections listed in the outline above. Skip a section if
   the evidence does not support it.
6. `## Implications and Recommendations` — practical recommendations for
   developers, organizations, or policymakers, as suits the topic.
7. `## Limitations and Open Questions` — missing evidence, contradictory
   findings, uncertain estimates, and areas that need more research.

RULES:
- Cite sources ONLY with inline bracket numbers matching the evidence above,
  like [1] or [2][3]. Never invent numbers and never write URLs yourself.
- Do NOT write a References section; it is added automatically.
- Use ONLY facts from the evidence. If the evidence is thin, say so honestly
  instead of guessing.
- Adapt depth to the topic and the available evidence: be comprehensive, but do
  not pad. A typical report is 700-1400 words.
- Write in clear Markdown: headings, bullet lists, bold for emphasis, and a
  table only when the data supports one.
- Output only the report Markdown, starting with the `# title` line.

Write the report now.
"""

    print("[WRITER] Calling LLM...\n")

    full_response = ""

    for chunk in llm.stream(prompt):

        text = content_to_text(chunk.content)

        if text:

            print(text, end="", flush=True)

            stream_writer({
                "type": "report_chunk",
                "content": text
            })

            full_response += text

    # Citation and formatting validation
    final_report = validate_report(full_response, sources)

    print("\n\n[WRITER] LLM response completed.")

    return {
        "draft_report": final_report
    }
