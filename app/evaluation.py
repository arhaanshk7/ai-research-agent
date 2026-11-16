import json
import uuid

from app.config import content_to_text, llm
from app.graph import graph


def build_initial_state(question: str) -> dict:
    return {
        "user_query": question,
        "research_plan": [],
        "sources": [],
        "research_results": [],
        "failed_claims": [],
        "fact_check_passed": True,
        "draft_report": "",
        "report_outline": "",
        "report_meta": {},
        "human_approved": False,
        "human_feedback": "",
        "follow_up_question": "",
        "follow_up_answer": "",
        "retry_count": 0,
    }


def run_research(question: str) -> dict:
    thread_id = str(uuid.uuid4())

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    graph.invoke(build_initial_state(question), config=config)

    values = graph.get_state(config).values

    return {
        "question": question,
        "report": values.get("draft_report", ""),
        "sources": values.get("sources", []),
        "research_results": values.get("research_results", []),
        "thread_id": thread_id,
    }


def target(inputs: dict) -> dict:
    return run_research(inputs["question"])


def judge_report(report: str, research_results: list[dict]) -> dict:
    evidence = "\n\n".join(
        f"[{index}] {result.get('title', '')}\n"
        f"URL: {result.get('url', '')}\n"
        f"{str(result.get('content', ''))[:2000]}"
        for index, result in enumerate(research_results, start=1)
    )

    prompt = f"""
You are a strict faithfulness judge. Extract every factual claim from the report
and check each claim ONLY against the retrieved evidence. Do not use outside
knowledge. Ignore the References section and citation numbers.

Status rules:
- "supported": evidence clearly confirms the claim.
- "partial": evidence confirms part of it, or is ambiguous.
- "unsupported": evidence does not support it or contradicts it.

REPORT:
{report}

RETRIEVED EVIDENCE:
{evidence}

Return ONLY JSON:
{{
  "claims": [
    {{"claim": "...", "status": "supported", "explanation": "..."}}
  ]
}}
"""

    response = llm.bind(response_mime_type="application/json").invoke(prompt)
    text = content_to_text(response.content).strip()
    text = text.replace("```json", "").replace("```", "").strip()
    claims = json.loads(text).get("claims", [])

    supported = sum(1 for claim in claims if claim.get("status") == "supported")
    partial = sum(1 for claim in claims if claim.get("status") == "partial")
    unsupported = sum(1 for claim in claims if claim.get("status") == "unsupported")
    total = len(claims)

    return {
        "claims": claims,
        "total_claims": total,
        "supported_claims": supported,
        "partial_claims": partial,
        "unsupported_claims": unsupported,
        "faithfulness": (supported / total * 100) if total else 0,
    }


def faithfulness_evaluator(run, example):
    outputs = run.outputs or {}

    judgment = judge_report(
        outputs.get("report", ""),
        outputs.get("research_results", []),
    )

    explanations = "\n".join(
        f"[{claim.get('status')}] {claim.get('claim')} - {claim.get('explanation')}"
        for claim in judgment["claims"]
        if claim.get("status") != "supported"
    )

    return [
        {"key": "faithfulness", "score": judgment["faithfulness"]},
        {"key": "supported_claims", "score": judgment["supported_claims"]},
        {"key": "partial_claims", "score": judgment["partial_claims"]},
        {"key": "unsupported_claims", "score": judgment["unsupported_claims"]},
        {"key": "judge_explanations", "value": explanations or "All claims supported."},
    ]
