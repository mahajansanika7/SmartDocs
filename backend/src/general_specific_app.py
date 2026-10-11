from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    ollama_chat,
    search_documents,
    generate_answer,
)

def classify_query(query: str) -> str:
    prompt = f"""
Classify the user's message into exactly one label:
GENERAL or DOCUMENT.

GENERAL means greetings, thanks, small talk, or questions that do not require information from the uploaded documents.
DOCUMENT means the user is asking for information that should be answered using the uploaded documents.

Return only GENERAL or DOCUMENT.

User message:
{query}
""".strip()

    label = ollama_chat(prompt).upper()
    return "GENERAL" if label.startswith("GENERAL") else "DOCUMENT"

def generate_general_answer(query: str):
    return ollama_chat(
    "Answer this casual/general user message briefly and naturally. "
    "Do not pretend to have access to documents.\n\n"
    f"User: {query}"
)

def main():
    print("SmartDocs - General vs Document Query")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        query_type = classify_query(query)
        print(f"Detected type: {query_type}")

        if query_type == "GENERAL":
            print("Answer:", generate_general_answer(query))
            print()
            continue

        matches = search_documents(query, top_k=3)

        if not matches:
            print("No relevant information found in the documents.\n")
            continue

        print("Answer:", generate_answer(query, matches))
        print("\nSources:")

        for match in matches:
            meta = match["metadata"]
            print(
                f"- {meta.get('document_name')} "
                f"page {meta.get('page')} "
                f"distance={match['distance']:.4f}"
            )

        print()


if __name__ == "__main__":
    main()
