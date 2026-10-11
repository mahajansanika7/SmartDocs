from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DIR = DATA_DIR / "chroma_db"
CACHE_DIR = DATA_DIR / "cache_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "qwen2.5:1.5b-instruct"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Chroma's default distance is squared L2 unless a collection specifies another metric.
# For the cache we use cosine distance explicitly.
CACHE_THRESHOLD = 0.15
RETRIEVAL_THRESHOLD = 0.75

TOP_K = 3
TEMPERATURE = 0.0



for directory in (DOCUMENTS_DIR, CHROMA_DIR, CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)


