from functools import lru_cache
from pathlib import Path
import hashlib
import re

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
# import ollama
import requests
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

from config import (
    CHROMA_DIR,
    CACHE_DIR,
    EMBEDDING_MODEL,
    OLLAMA_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_THRESHOLD,
)


@lru_cache(maxsize=1)
def get_embedder():
    """Load the embedding model once and reuse it."""
    return SentenceTransformer(EMBEDDING_MODEL)


def get_client(db_path: Path):
    return chromadb.PersistentClient(path=str(db_path))


def get_document_collection():
    client = get_client(CHROMA_DIR)
    return client.get_or_create_collection(
        name="documents",
        metadata={"hnsw:space": "cosine"},
    )


def get_cache_collection():
    client = get_client(CACHE_DIR)
    return client.get_or_create_collection(
        name="response_cache",
        metadata={"hnsw:space": "cosine"},
    )


def extract_pdf_pages(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        pages.append((page_number, page.extract_text()))

    return pages


def chunk_text(text: str, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Simple character-based overlapping chunker."""
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(0, end - overlap)

    return chunks


def make_id(*parts):
    raw = "||".join(map(str, parts))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ingest_pdf(pdf_path: Path):
    collection = get_document_collection()
    pages = extract_pdf_pages(pdf_path)

    all_chunks = []
    all_metadata = []
    all_ids = []

    for page_number, page_text in pages:
        chunks = chunk_text(page_text)

        for chunk_number, chunk in enumerate(chunks, start=1):
            all_chunks.append(chunk)
            all_metadata.append({
                "document_name": pdf_path.name,
                "page": page_number,
                "chunk": chunk_number,
                "source": str(pdf_path.name),
            })
            all_ids.append(make_id(pdf_path.name, page_number, chunk_number, chunk))

    if not all_chunks:
        raise ValueError(f"No extractable text found in {pdf_path.name}")

    embeddings = get_embedder().encode(
        all_chunks,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).tolist()

    collection.upsert(
        ids=all_ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadata,
    )

    return len(all_chunks)


def search_documents(query: str,  document_name, top_k=3):
    collection = get_document_collection()
    embedding = get_embedder().encode(
        [query],
        normalize_embeddings=True,
    )[0].tolist()

    result = collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
        where={"document_name": document_name} if document_name else None,
        include=["documents", "metadatas", "distances"],
    )

    matches = []
    docs = result.get("documents", [[]])[0]
    metas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, meta, distance in zip(docs, metas, distances):
        distance = float(distance)
        
        if distance<=RETRIEVAL_THRESHOLD:
            matches.append({
                "document": doc,
                "metadata": meta,
                "distance": float(distance),
            })

    return matches

def ollama_chat(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.0,
            },
        },
        timeout=300,
    )

    response.raise_for_status()

    data = response.json()
    return data["message"]["content"].strip()

def generate_answer(query: str, matches):
    context_parts = []

    for i, match in enumerate(matches, start=1):
        meta = match["metadata"]
        context_parts.append(
            f"[Source {i}: {meta.get('document_name')} - page {meta.get('page')}]\n"
            f"{match['document']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the supplied context.
If the context does not contain enough information, say:
"I could not find enough information in the provided documents."

Do not invent facts.
Keep the answer concise and clear.
Mention the relevant source document and page when possible.

Context:
{context}

User question:
{query}
""".strip()

    return ollama_chat(prompt)

def answer_query(query: str, document: str):
    top_k=3
    matches = search_documents(query, document, top_k=top_k)

    if not matches:
        return {
            "answer": "I could not find relevant information in the provided documents.",
            "source": "retrieval",
            "sources": []
        }
    sources=[]

    answer = generate_answer(query, matches)

    for match in matches:
        meta=match["metadata"]
        
        sources.append({
            "document": meta["document_name"],
            "page": meta["page"],
            "chunk": meta["chunk"]
       } )
        
    return {
        "answer": answer,
        "source": "rag",
        "sources": sources
    }
    
