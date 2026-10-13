# SmartDocs — AI-Powered Document Assistant

SmartDocs is a RAG-based application that lets users upload PDF documents and ask questions about their content. It uses local LLM inference, semantic search, and response caching to generate relevant answers.

## Features

- PDF ingestion and overlapping text chunking
- Semantic search using `all-MiniLM-L6-v2` and ChromaDB
- Local LLM inference with Ollama and `qwen2.5:1.5b-instruct`
- Cached responses and query classification
- Angular frontend and FastAPI backend
- JWT authentication and SQL Server query history

## Tech Stack

**Frontend:** Angular, TypeScript  
**Backend:** Python, FastAPI  
**AI/RAG:** Ollama, ChromaDB, Sentence Transformers  
**Database:** SQL Server

## Project Structure

```text
SmartDocs/
├── backend/
│   ├── src/
│   ├── .env
│   └── requirements.txt
└── frontend/
```

## Setup

### 1. Backend

From the `backend` directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Configure `backend/.env` with your own values:

```dotenv
JWT_SECRET_KEY=your-generated-secret-key
SMARTDOCS_CONNECTION_STRING=your-sql-server-connection-string
```

Generate a secure JWT key with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Replace both placeholders with your actual values. Install Ollama and download the model:

```powershell
ollama pull qwen2.5:1.5b-instruct
```

Start the backend from `backend/`:

```powershell
python -m uvicorn src.api:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend

From the `frontend` directory:

```powershell
npm install
npx ng serve
```

Open `http://localhost:4200`.

## Security

Do not commit `.env`, uploaded documents, ChromaDB data, or other sensitive files to GitHub. Ensure these are covered by `.gitignore`.
