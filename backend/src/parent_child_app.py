from pathlib import Path
import hashlib
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import chromadb
from common import (
    get_embedder,
    extract_pdf_pages,
    chunk_text,
    generate_answer,
    make_id,
)
from config import DOCUMENTS_DIR, CHROMA_DIR


PARENT_SIZE = 1800
PARENT_OVERLAP = 200
CHILD_SIZE = 450
CHILD_OVERLAP = 100


def get_parent_child_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name="parent_child_documents",
        metadata={"hnsw:space": "cosine"},
    )


def build_parent_child_index():
    collection = get_parent_child_collection()

    ids = []
    documents = []
    metadatas = []

    for pdf_path in sorted(DOCUMENTS_DIR.glob("*.pdf")):
        pages = extract_pdf_pages(pdf_path)

        for page_number, page_text in pages:
            parents = chunk_text(page_text, PARENT_SIZE, PARENT_OVERLAP)

            for parent_number, parent in enumerate(parents, start=1):
                children = chunk_text(parent, CHILD_SIZE, CHILD_OVERLAP)

                parent_id = make_id(
                    pdf_path.name,
                    page_number,
                    "parent",
                    parent_number,
                    parent,
                )

                for child_number, child in enumerate(children, start=1):
                    ids.append(make_id(parent_id, child_number, child))
                    documents.append(child)
                    metadatas.append({
                        "document_name": pdf_path.name,
                        "page": page_number,
                        "parent_id": parent_id,
                        "parent_text": parent,
                        "parent_number": parent_number,
                        "child_number": child_number,
                    })

    if not documents:
        raise ValueError("No PDF text found.")

    embeddings = get_embedder().encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(documents)

def build_parent_child_index_uploaded_pdf(pdf_path: Path):
    collection = get_parent_child_collection()

    # Remove old chunks for this document, if it is being re-uploaded
    existing = collection.get(
        where={"document_name": pdf_path.name},
        include=[]
    )

    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    ids = []
    documents = []
    metadatas = []

    pages = extract_pdf_pages(pdf_path)

    for page_number, page_text in pages:

        parents = chunk_text( page_text, PARENT_SIZE, PARENT_OVERLAP )

        for parent_number, parent in enumerate( parents, start=1 ):

            children = chunk_text( parent, CHILD_SIZE, CHILD_OVERLAP )

            parent_id = make_id( pdf_path.name, page_number, "parent", parent_number, parent,)

            for child_number, child in enumerate( children, start=1 ):

                ids.append(
                    make_id( parent_id, child_number, child )
                )

                documents.append(child)

                metadatas.append({
                    "document_name": pdf_path.name,
                    "page": page_number,
                    "parent_id": parent_id,
                    "parent_text": parent,
                    "parent_number": parent_number,
                    "child_number": child_number,
                })

    if not documents:
        raise ValueError(
            f"No extractable text found in {pdf_path.name}"
        )

    embeddings = get_embedder().encode(
        documents,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(documents)

def search_parent_child(query: str, top_k: int, document):
    collection = get_parent_child_collection()

    if collection.count() == 0:
        return []

    query_embedding = get_embedder().encode(
        [query],
        normalize_embeddings=True,
    )[0].tolist()

    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"document_name": document} if document else None,
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for child, metadata, distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        matches.append({
            "document": child,
            "metadata": metadata,
            "distance": float(distance),
        })

    return matches

def get_parent_matches(query: str, top_k: int, document):

    child_matches = search_parent_child(
        query,
        top_k,
        document
    )

    parent_matches = []
    seen_parent_ids = set()

    for match in child_matches:

        parent_id = match["metadata"]["parent_id"]

        if parent_id in seen_parent_ids:
            continue

        seen_parent_ids.add(parent_id)

        parent_matches.append({
            "document": match["metadata"]["parent_text"],
            "metadata": match["metadata"],
            "distance": match["distance"],
        })

    return parent_matches

def main():
    print("Building parent-child index...")
    count = build_parent_child_index()
    print(f"Indexed {count} child chunks.\n")

    print("SmartDocs - Parent/Child RAG")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        matches = get_parent_matches(query, top_k=3)

        if not matches:
            print("No relevant information found.\n")
            continue

        # Use the matched parent context rather than only the tiny child.
        

        answer = generate_answer(query, matches)

        print("\nAnswer:", answer)
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
