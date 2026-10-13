from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import CACHE_THRESHOLD
from common import get_cache_collection, get_embedder, search_documents, generate_answer, make_id

def get_cached_answer(query: str, document: str):
    collection = get_cache_collection()

    if collection.count() == 0:
        return None

    cache_text=f"{document}::{query}"
    embedding = get_embedder().encode(
        [cache_text],
        normalize_embeddings=True,
    )[0].tolist()

    result = collection.query(
        query_embeddings=[embedding],
        n_results=1,
        include=["documents", "metadatas", "distances"],
    )
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    if not documents:
        return None

    distance = float(distances[0])

    if distance <= CACHE_THRESHOLD:
        return {
            "answer": documents[0],
            "distance": distance,
            "metadata": metadatas[0],
        }

    return None


def save_cached_answer(query: str, answer: str, document: str):
    collection = get_cache_collection()
    cache_text=f"{document}::{query}"
    embedding = get_embedder().encode(
        [cache_text],
        normalize_embeddings=True,
    )[0].tolist()

    cache_id = make_id(query)

    collection.upsert(
        ids=[cache_id],
        documents=[answer],
        embeddings=[embedding],
        metadatas=[{"query": query}],
    )

def main():
    print("SmartDocs - Cached RAG")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        cached = get_cached_answer(query)

        if cached:
            print(f"\nCACHE HIT (distance={cached['distance']:.4f})")
            print(cached["answer"])
            print()
            continue

        print("\nCACHE MISS -> running document retrieval...")

        matches = search_documents(query, top_k=3)

        if not matches:
            print("No relevant document chunks found.\n")
            continue

        answer = generate_answer(query, matches)
        save_cached_answer(query, answer)

        print("\nCACHE MISS -> generated answer and saved it to cache.")
        print(answer)
        print()


if __name__ == "__main__":
    main()
