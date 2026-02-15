"""
FastAPI backend — HTTP API for the regulatory Q&A system.

This wraps our multi-agent pipeline in a web server so the React
frontend (or any HTTP client) can send questions and get answers.

Endpoints:
  POST /api/ask     — Submit a question, get an answer with sources
  GET  /api/health  — Check if the server is running

Run with:
  uvicorn main:app --reload --port 8000
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph import ask_question

load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Regulatory Q&A API",
    description="Multi-agent RAG system for regulatory compliance questions",
    version="1.0.0",
)

# CORS (Cross-Origin Resource Sharing) middleware.
# Without this, the React frontend (running on a different port/domain)
# would be BLOCKED from calling our API.
# Set CORS_ORIGINS env var as comma-separated URLs for production.
_default_origins = ["http://localhost:5173", "http://localhost:3000"]
_cors_origins = os.getenv("CORS_ORIGINS")
allowed_origins = [o.strip() for o in _cors_origins.split(",")] if _cors_origins else _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request and Response models ---
# These define the exact shape of JSON the API expects and returns.
# Pydantic validates incoming data automatically — if someone sends
# a request without a "question" field, they get a clear error.

class QueryRequest(BaseModel):
    """What the frontend sends to us."""
    question: str


class SourceDocument(BaseModel):
    """A single source document in the response."""
    regulation: str
    page: int
    content: str


class VerificationClaim(BaseModel):
    """A single verified claim from the compliance checker."""
    text: str
    status: str       # SUPPORTED, PARTIAL, or UNSUPPORTED
    source: str | None


class QueryResponse(BaseModel):
    """What we send back to the frontend."""
    answer: str
    sources: list[SourceDocument]
    confidence: float
    query_type: str
    verification: dict


# --- Endpoints ---

@app.post("/api/ask", response_model=QueryResponse)
def ask(request: QueryRequest):
    """
    Main endpoint — submit a regulatory question.

    The frontend sends: {"question": "What does SR 11-7 require?"}
    We return: {"answer": "...", "sources": [...], "confidence": 0.92, ...}

    Behind the scenes, this calls the full agent pipeline:
    Router -> Retriever -> Synthesizer -> Compliance Checker
    """
    result = ask_question(request.question)
    return QueryResponse(**result)


@app.get("/api/health")
def health():
    """
    Health check — is the server running?

    Useful for monitoring and for Docker health checks.
    The frontend can call this on load to verify the backend is up.
    """
    return {"status": "healthy"}
