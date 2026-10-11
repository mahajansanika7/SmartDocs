from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import answer_query


def main():
    print("SmartDocs RAG CLI")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        try:
            result = answer_query(query, top_k=3)

            print(f"\nSource mode: {result['source']}")
            print(f"Answer: {result['answer']}")

            if result["matches"]:
                print("\nRetrieved sources:")
                for source in result["sources"]:
                    # meta = match["metadata"]
                    print(
                        f"{source['document']}"
                        f"(Page {source['page']})"
                        # f"- {meta.get('document_name')} "
                        # f"(page {meta.get('page')}, "
                        # f"distance={match['distance']:.4f})"
                    )

            print()
        except Exception as exc:
            print(f"\nERROR: {exc}\n")


if __name__ == "__main__":
    main()
