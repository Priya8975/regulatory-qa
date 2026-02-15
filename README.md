# Regulatory Q&A — Multi-Agent RAG System

A multi-agent AI system that answers regulatory compliance questions across financial and insurance frameworks (SR 11-7, NIST AI RMF, ISO 42001, NAIC Model Bulletin, Colorado SB21-169) using Retrieval-Augmented Generation with source citations and hallucination detection.

**Author:** Priya More

---

## Problem

Financial institutions and insurance companies must comply with a growing number of AI and model risk regulations. Compliance teams spend significant time manually searching through lengthy regulatory documents to find relevant guidance. This system automates that process — delivering accurate, cited answers in seconds while flagging any unsupported claims.

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 React Frontend                   │
│       (Chat UI + Sources + Confidence)           │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Backend                      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│           LangGraph Orchestrator                 │
│                                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────────┐  │
│  │  Router    │→│ Retriever │→│  Synthesizer  │  │
│  │  Agent     │ │  Agent    │ │  Agent        │  │
│  └───────────┘ └───────────┘ └───────┬───────┘  │
│                                      │           │
│                              ┌───────▼───────┐   │
│                              │  Compliance   │   │
│                              │  Checker      │   │
│                              └───────────────┘   │
└──────────────────┬──────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
┌──────────────┐    ┌─────────────────┐
│  ChromaDB    │    │   LangSmith     │
│ Vector Store │    │  Observability  │
└──────────────┘    └─────────────────┘
```

---

## How It Works

The system uses four specialized agents orchestrated through LangGraph:

| Agent | Role |
|---|---|
| **Router** | Classifies the user query into LOOKUP, COMPARE, CHECKLIST, or EXPLAIN and routes accordingly |
| **Retriever** | Fetches relevant regulatory passages from ChromaDB using query-type-specific retrieval strategies |
| **Synthesizer** | Generates a coherent answer with inline source citations grounded in retrieved passages |
| **Compliance Checker** | Validates every claim against source documents, flags unsupported statements, and returns a confidence score |

If the Compliance Checker's confidence score falls below 0.7, the system automatically retries retrieval with adjusted parameters (up to 2 retries).

---

## Regulations Covered

| Regulation | Domain | Issuer |
|---|---|---|
| SR 11-7 | Model Risk Management | Federal Reserve / OCC |
| NIST AI RMF 1.0 | AI Risk Management | NIST |
| ISO 42001 | AI Management Systems | ISO |
| NAIC Model Bulletin | Insurance AI Governance | NAIC |
| Colorado SB21-169 | Insurance AI Regulation | State of Colorado |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agents & Orchestration | LangChain, LangGraph |
| Observability & Evaluation | LangSmith |
| LLM | OpenAI GPT-4o / GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector Store | ChromaDB |
| Backend API | FastAPI, Uvicorn |
| Frontend | React, Vite, Axios |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | pytest, httpx |
| Linting | Ruff |

---

## Project Structure

```
regulatory-qa/
├── .github/
│   └── workflows/
│       └── ci.yml                  # CI pipeline (lint, test, build)
├── backend/
│   ├── agents/
│   │   ├── state.py                # Shared agent state definition
│   │   ├── router.py               # Query classification agent
│   │   ├── retriever.py            # RAG retrieval agent
│   │   ├── synthesizer.py          # Answer generation agent
│   │   └── compliance_checker.py   # Hallucination detection agent
│   ├── ingestion/
│   │   ├── ingest.py               # PDF loading and vector store creation
│   │   └── retriever.py            # Vector store search utilities
│   ├── tests/
│   │   ├── test_agents.py          # Agent unit tests (mocked LLM calls)
│   │   └── test_api.py             # API endpoint tests
│   ├── graph.py                    # LangGraph workflow definition
│   ├── main.py                     # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   ├── SourcePanel.jsx
│   │   │   └── ConfidenceBadge.jsx
│   │   ├── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── Dockerfile
├── data/                           # Regulatory PDFs
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 20+
- OpenAI API key
- LangSmith API key (optional, for observability — free at [smith.langchain.com](https://smith.langchain.com))

### 1. Clone the repository

```bash
git clone https://github.com/Priya8975/regulatory-qa.git
cd regulatory-qa
```

### 2. Set up the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example env file and fill in your keys:

```bash
cp backend/.env.example backend/.env
```

```
OPENAI_API_KEY=your-openai-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=regulatory-qa
```

### 4. Add regulatory documents

Place PDF files in the `data/` directory. Supported documents:
- SR 11-7 (Federal Reserve)
- NIST AI 100-1 (AI Risk Management Framework)
- NAIC Model Bulletin
- Colorado SB21-169

### 5. Run document ingestion

```bash
cd backend
python -m ingestion.ingest
```

### 6. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

### 7. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Docker (alternative)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

## Live Demo

- **Frontend:** [https://regulatory-qa.vercel.app](https://regulatory-qa.vercel.app)
- **Backend API:** [https://regulatory-qa-backend.onrender.com](https://regulatory-qa-backend.onrender.com)
- **API Docs:** [https://regulatory-qa-backend.onrender.com/docs](https://regulatory-qa-backend.onrender.com/docs)

> Note: The backend runs on Render's free tier and may take ~30 seconds to wake up on the first request after inactivity.

---

## Sample Questions

**Lookup**
> "What are the three lines of defense described in SR 11-7?"

**Compare**
> "How do SR 11-7 and NIST AI RMF differ in their approach to model validation?"

**Checklist**
> "What steps must an insurer follow under the NAIC Model Bulletin before deploying an AI model?"

**Explain**
> "Explain the concept of effective challenge in model risk management."

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ask` | Submit a regulatory question and get an answer with sources |
| `GET` | `/api/health` | Health check and document count |

### Example request

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What does SR 11-7 require for model validation?"}'
```

### Example response

```json
{
  "answer": "SR 11-7 requires that model validation be conducted by parties independent of the model development process... [Source: SR 11-7, Page 12]",
  "sources": [
    {
      "regulation": "SR 11-7",
      "page": 12,
      "content": "Banks should ensure that model validation is conducted..."
    }
  ],
  "confidence": 0.92,
  "query_type": "LOOKUP"
}
```

---

## Testing

Run the backend test suite (16 tests, all mocked — no API key needed):

```bash
cd backend
python -m pytest tests/ -v
```

Run the linter:

```bash
cd backend
ruff check .
```

---

## CI/CD

The GitHub Actions pipeline runs on every push and pull request to `main`:

- **Linting** — Ruff checks for code quality
- **Backend Tests** — pytest runs all unit and integration tests
- **Frontend Build** — Verifies the React app compiles successfully

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Multi-agent over single prompt | Specialized agents are easier to test, debug, and improve independently |
| Compliance Checker agent | Critical in regulated industries where hallucinated guidance can have serious consequences |
| Metadata-filtered retrieval | Enables targeted search within specific regulations for LOOKUP queries |
| Confidence-based retry loop | Automatically re-retrieves when the system detects low-confidence answers |
| LangSmith integration | Provides the audit trail and observability that financial regulators expect |

---

## Future Improvements

- Add support for additional regulations (EU AI Act, Basel III/IV, SOX)
- Implement conversational memory for multi-turn follow-up questions
- Add user authentication and role-based access
- Fine-tune embeddings on regulatory corpus for better retrieval
- Add a feedback loop where users can rate answer quality

---

Built by **Priya More**
