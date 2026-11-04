from typing import TypedDict

class ResearchState(TypedDict):
    user_query: str
    research_plan: list[str]

    sources: list[dict]
    research_results: list[dict]

    failed_claims: list[str]
    fact_check_passed: bool

    draft_report: str

    report_outline: str
    report_meta: dict

    human_approved: bool
    human_feedback: str

    follow_up_question: str
    follow_up_answer: str

    retry_count: int
