import json

from dotenv import load_dotenv
from langsmith import evaluate

from app.evaluation import faithfulness_evaluator

load_dotenv()


DATASET = "research_questions_20"
OUTPUT_FILE = "eval_results_20.jsonl"


def load_results() -> dict:
    results = {}

    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                item = json.loads(line)
                results[item["question"]] = item

    return results


RESULTS = load_results()


def cached_target(inputs: dict) -> dict:
    return RESULTS[inputs["question"]]


def main():
    print("cached results:", len(RESULTS))

    results = evaluate(
        cached_target,
        data=DATASET,
        evaluators=[faithfulness_evaluator],
        experiment_prefix="research-faithfulness",
        max_concurrency=1,
        metadata={"judge": "gemini", "source": OUTPUT_FILE},
    )

    print("experiment:", results.experiment_name)
    print("url:", results.url)
    print("evaluated:", len(results))


if __name__ == "__main__":
    main()
