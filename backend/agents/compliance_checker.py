"""
Compliance Checker Agent — verifies the answer is grounded in sources.

This is the last agent in the pipeline. It takes the Synthesizer's answer
and checks every claim against the retrieved source documents.

Why this matters:
- LLMs can "hallucinate" — generate plausible-sounding but incorrect info
- In regulated industries, incorrect compliance guidance is dangerous
- This agent catches unsupported claims before they reach the user

Output includes:
- A list of claims with their verification status
- An overall confidence score (0.0 to 1.0)
- A summary of the verification
"""

import json

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.state import AgentState

load_dotenv()

# Use gpt-4o-mini for verification — it's a structured evaluation task
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _llm

VERIFICATION_PROMPT = """You are a fact-checker for regulatory compliance content.

Your job: Compare the ANSWER against the SOURCE DOCUMENTS and verify each claim.

For each distinct claim or statement in the answer, determine:
- SUPPORTED: The claim is directly backed by text in the source documents
- PARTIAL: The claim is related to source content but not an exact match
- UNSUPPORTED: No source document supports this claim

SOURCE DOCUMENTS:
{sources}

ANSWER TO VERIFY:
{answer}

Respond with valid JSON only (no markdown, no extra text):
{{
  "claims": [
    {{"text": "the claim text", "status": "SUPPORTED", "source": "Regulation Name, Page X"}},
    {{"text": "another claim", "status": "UNSUPPORTED", "source": null}}
  ],
  "confidence": 0.85,
  "summary": "X of Y claims are supported by source documents"
}}

The confidence score should be:
- 1.0 if all claims are SUPPORTED
- 0.0 if all claims are UNSUPPORTED
- Proportional based on the ratio of SUPPORTED claims"""


def format_sources_for_check(docs: list) -> str:
    """Format source documents for the verification prompt."""
    formatted = []
    for doc in docs:
        regulation = doc.metadata.get("regulation", "Unknown")
        page = doc.metadata.get("page", "?")
        formatted.append(f"[{regulation} | Page {page}]\n{doc.page_content}")

    return "\n\n".join(formatted)


def parse_verification_response(response_text: str) -> dict:
    """
    Parse the LLM's JSON response. Handle cases where it might
    return malformed JSON or add extra text around the JSON.
    """
    text = response_text.strip()

    # Sometimes LLMs wrap JSON in markdown code blocks
    if text.startswith("```"):
        # Remove ```json and ``` markers
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If parsing fails, return a safe default
        return {
            "claims": [],
            "confidence": 0.5,
            "summary": "Could not parse verification response",
        }


def compliance_checker_agent(state: AgentState) -> AgentState:
    """
    Verify that the answer is grounded in source documents.

    Input state needs: answer, retrieved_docs
    Output state adds: verification
    """
    answer = state["answer"]
    docs = state["retrieved_docs"]

    # Format sources for the prompt
    sources_text = format_sources_for_check(docs)

    # Build the verification prompt
    prompt = VERIFICATION_PROMPT.format(
        sources=sources_text,
        answer=answer,
    )

    # Call the LLM
    response = get_llm().invoke(prompt)

    # Parse the JSON response
    verification = parse_verification_response(response.content)

    state["verification"] = verification

    return state
