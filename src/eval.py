import json
import re
import sys
from src.rag import retrieve
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1", temperature=0.2)
judge = ChatOllama(model="llama3.1", temperature=0.0)  # temp=0 for consistent scoring

# The prompt under test. Pass a different one as sys.argv[1] label to compare versions.
PROMPT_VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"

DIAGNOSIS_PROMPT = """Answer the question directly using ONLY the context below. Structure
your response as exactly two parts:
1) A direct 1-2 sentence answer to the question itself, first.
2) Supporting reasoning grounded in the context, citing the source document by name.
If the context doesn't fully address this specific question, say so explicitly instead of
guessing or padding with tangential detail.

Context:
{context}

Question: {question}"""


def extract_score(text: str) -> float:
    """Pull a 0-1 score out of the judge's response, defaulting to 0 if unparseable."""
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return 0.0
    val = float(match.group(1))
    return val / 10 if val > 1 else val  # handles judge answering "8/10" style


def score_faithfulness(context: str, answer: str) -> float:
    prompt = f"""You are grading whether an AI-generated answer is faithful to its source
context, i.e. every claim in the answer is actually supported by the context (no invented
details).

Context:
{context}

Answer:
{answer}

Respond with ONLY a single number from 0 to 1 (e.g. 0.8), where 1 = fully supported by
context, 0 = mostly invented/unsupported. No explanation, just the number."""
    result = judge.invoke(prompt).content
    return extract_score(result)


def score_relevancy(question: str, answer: str) -> float:
    prompt = f"""You are grading whether an answer actually addresses the question asked,
regardless of whether the answer is correct.

Question: {question}
Answer: {answer}

Respond with ONLY a single number from 0 to 1 (e.g. 0.9), where 1 = directly and fully
addresses the question, 0 = off-topic or non-responsive. No explanation, just the number."""
    result = judge.invoke(prompt).content
    return extract_score(result)


def main():
    with open("eval_set.json") as f:
        eval_items = json.load(f)

    results = []
    for item in eval_items:
        question = item["question"]
        docs = retrieve(question, k=3)
        context = "\n\n".join(f"[{d.metadata['source']}]\n{d.page_content}" for d in docs)

        answer = llm.invoke(DIAGNOSIS_PROMPT.format(context=context, question=question)).content

        faithfulness = score_faithfulness(context, answer)
        relevancy = score_relevancy(question, answer)

        results.append({
            "question": question,
            "answer": answer,
            "sources": [d.metadata["source"] for d in docs],
            "faithfulness": faithfulness,
            "relevancy": relevancy,
        })
        print(f"[{len(results)}/{len(eval_items)}] faithfulness={faithfulness:.2f} "
              f"relevancy={relevancy:.2f} — {question[:60]}")

    avg_faith = sum(r["faithfulness"] for r in results) / len(results)
    avg_rel = sum(r["relevancy"] for r in results) / len(results)

    print(f"\n=== PROMPT VERSION: {PROMPT_VERSION} ===")
    print(f"Average faithfulness: {avg_faith:.3f}")
    print(f"Average relevancy:    {avg_rel:.3f}")

    # Append this run to a running log so prompt versions are comparable over time
    log_entry = {"version": PROMPT_VERSION, "avg_faithfulness": avg_faith, "avg_relevancy": avg_rel}
    try:
        with open("eval_results_log.json") as f:
            log = json.load(f)
    except FileNotFoundError:
        log = []
    log.append(log_entry)
    with open("eval_results_log.json", "w") as f:
        json.dump(log, f, indent=2)

    with open(f"eval_details_{PROMPT_VERSION}.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nFull results saved to eval_details_{PROMPT_VERSION}.json")
    print(f"Score history saved to eval_results_log.json")


if __name__ == "__main__":
    main()
