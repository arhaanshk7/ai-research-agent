
from concurrent.futures import ThreadPoolExecutor, as_completed

import os
import re
from dotenv import load_dotenv
from tavily import TavilyClient
from flashrank import Ranker, RerankRequest

from app.state import ResearchState
from app.config import llm, content_to_text


load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")

client = TavilyClient(tavily_api_key)

# Cap on merged (previous + new) results so the writer prompt stays bounded
MAX_MERGED_RESULTS = 24

# Maximum number of documents to retain
TOP_K_RESULTS = 8

# Initialize FlashRank reranker
ranker = Ranker()


def search_question(question):
    response = client.search(
        query=question,
        search_depth="basic",
        max_results=3
    )

    return response["results"]


def parse_query_list(text: str) -> list[str]:
    """Extract 1-3 short search queries from an LLM response."""

    queries = []

    for line in text.splitlines():
        line = re.sub(r"^(?:[-*•]\s*|\d+[.)]\s*)", "", line.strip()).strip()

        if line:
            queries.append(line[:160])

    return queries[:3]


def generate_feedback_queries(query: str, feedback: str) -> list[str]:
    """Turn reviewer feedback into targeted web search queries."""

    prompt = f"""
You are a research assistant preparing targeted web searches.

TOPIC:
{query}

REVIEWER FEEDBACK on the current report:
{feedback}

Return 2-3 short web search queries (one per line) that would find fresh
evidence to address this feedback. Focus on what the feedback asks for.
Return only the queries - no numbering, no explanation.
"""

    try:
        response = llm.invoke(prompt)
        queries = parse_query_list(content_to_text(response.content))
        return queries or [feedback.strip()[:160]]
    except Exception as error:
        print(f"[RESEARCHER] Query generation failed ({error}), using feedback as query.")
        return [feedback.strip()[:160]]


def merge_results(previous: list[dict], new: list[dict]) -> list[dict]:
    """New evidence first (it targets the feedback), then previous research.

    Deduplicated by URL so previous research is preserved, not repeated.
    """

    merged = []
    seen = set()

    for result in list(new) + list(previous):

        url = str(result.get("url") or "").strip()

        if not url or url in seen:
            continue

        seen.add(url)
        merged.append(result)

        if len(merged) >= MAX_MERGED_RESULTS:
            break

    return merged


def rerank_results(query: str, results: list[dict]) -> list[dict]:
    """Rank documents by relevance and retain the top K results."""

    if not results:
        return []

    passages = []

    for index, result in enumerate(results):
        title = str(result.get("title") or "")
        content = str(result.get("content") or "")

        passages.append({
            "id": index,
            "text": f"{title}\n{content}",
            "meta": {"url": result.get("url", "")}
        })

    request = RerankRequest(
        query=query,
        passages=passages
    )

    ranked_results = ranker.rerank(request)

    return [
        results[int(item["id"])]
        for item in ranked_results[:TOP_K_RESULTS]
    ]


def researcher_node(state: ResearchState):

    print("\n[RESEARCHER] Starting...")

    feedback = str(state.get("human_feedback") or "").strip()

    if feedback:
        # Revision: keep previous research, search only for evidence that
        # addresses the reviewer feedback.
        queries = generate_feedback_queries(state["user_query"], feedback)
        print(f"[RESEARCHER] Revision queries: {queries}")
    else:
        queries = [
            question.strip()
            for question in state["research_plan"]
            if question and question.strip()
        ]

    previous_results = state.get("research_results", [])

    # Run all searches in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:

        futures = [
            executor.submit(search_question, question)
            for question in queries
        ]

        new_results = []

        for future in as_completed(futures):

            results = future.result()

            print("[RESEARCHER] Search completed.")

            new_results.extend(results)

    # Preserve previous research while adding new evidence (deduped by URL)
    research_results = merge_results(previous_results, new_results)

    # Rank documents and retain the top 8
    research_results = rerank_results(
        state["user_query"],
        research_results
    )

    sources = []
    seen_sources = set()

    for result in research_results:
        url = str(result.get("url") or "").strip()
        if not url or url in seen_sources:
            continue
        seen_sources.add(url)
        sources.append({
            "title": result.get("title"),
            "url": url
        })

    return {
        "research_results": research_results,
        "sources": sources,
        "retry_queries": queries if feedback else [],
        "retry_count": state.get("retry_count", 0) + 1
    }
