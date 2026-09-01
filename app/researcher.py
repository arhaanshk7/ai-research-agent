from concurrent.futures import ThreadPoolExecutor, as_completed

import os
from dotenv import load_dotenv
from tavily import TavilyClient

from app.state import ResearchState


load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")

client = TavilyClient(tavily_api_key)


def search_question(question):
    response = client.search(
        query=question,
        search_depth="basic",
        max_results=3
    )

    return response["results"]


def researcher_node(state: ResearchState):

    print("\n[RESEARCHER] Starting...")

    research_results = []
    sources = []

    # Keep only valid research questions
    queries = [
        question.strip()
        for question in state["research_plan"]
        if question and question.strip()
    ]

    # Add human feedback if it exists and is not empty
    if state.get("human_feedback"):
        feedback = state["human_feedback"].strip()

        if feedback:
            queries.append(feedback)

    # Run all searches in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:

        futures = [
            executor.submit(search_question, question)
            for question in queries
        ]

        for future in as_completed(futures):

            results = future.result()

            print("[RESEARCHER] Search completed.")

            research_results.extend(results)

            for result in results:
                sources.append({
                    "title": result.get("title"),
                    "url": result.get("url")
                })

    return {
        "research_results": research_results,
        "sources": sources,
        "retry_count": state.get("retry_count", 0) + 1
    }