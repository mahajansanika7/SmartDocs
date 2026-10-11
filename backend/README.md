# SmartDocs - Current RAG Project

This is the cleaned-up version of the RAG project described in the original notes.

## Current features

- PDF ingestion
- overlapping text chunks
- `all-MiniLM-L6-v2` embeddings
- persistent ChromaDB
- local LLM through Ollama
- Qwen2.5 1.5B instruct model
- cached responses using a separate ChromaDB
- general vs document-query classification
- parent-child retrieval experiment

## Hardware target

Designed to be lightweight enough for an 8 GB RAM development laptop.

The generative LLM is intentionally small:

`qwen2.5:1.5b-instruct`

The embedding model is:

`sentence-transformers/all-MiniLM-L6-v2`

## Setup

### 1. Install Python

Use Python 3.10 or 3.11.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the commands from Command Prompt instead:

```cmd
.venv\Scripts\activate
```

### 3. Install packages

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama for Windows from:

https://ollama.com/download/windows

After installation, verify:

```powershell
ollama --version
```

### 5. Download the model

```powershell
ollama pull qwen2.5:1.5b-instruct
```

Test it:

```powershell
ollama run qwen2.5:1.5b-instruct
```

Type:

```text
Explain what RAG is in one sentence.
```

Then type `/bye`.

### 6. Add a PDF

Put a text-based PDF inside:

```text
data/documents/
```

Example:

```text
data/documents/company_policy.pdf
```

### 7. Build the vector database

From the project root:

```powershell
python src/ingest.py
```

This creates the persistent ChromaDB data under:

```text
data/chroma_db/
```

### 8. Run the current RAG application

```powershell
python src/app.py
```

Ask something that is answered by your PDF.

Type:

```text
exit
```

to stop.

## Other experiments

Cached RAG:

```powershell
python src/cached_app.py
```

General vs document query:

```powershell
python src/general_specific_app.py
```

Parent-child RAG:

```powershell
python src/parent_child_app.py
```

## Important

Do not commit these directories to GitHub:

```text
data/chroma_db/
data/cache_db/
data/documents/
```

The `.gitignore` already excludes them.

## Next development direction

This is intentionally not the final architecture.

Next steps:

1. Convert the scripts into a FastAPI backend.
2. Add PostgreSQL for users/documents/conversations.
3. Add authentication.
4. Add document/source citations.
5. Improve parent-child retrieval.
6. Add retrieval and latency evaluation.
7. Add Pytest.
8. Dockerize the backend/database after the application works locally.
