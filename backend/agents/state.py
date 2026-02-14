"""
Shared state definition for the multi-agent system.

All agents read from and write to this same state object.
It gets passed through the LangGraph pipeline:

  Router -> Retriever -> Synthesizer -> Compliance Checker

Each agent reads what it needs and adds its own output.
"""

from typing import TypedDict


class AgentState(TypedDict):
    # The user's original question (set at the start, never changes)
    query: str

    # What type of question is this? Set by the Router agent.
    # One of: "LOOKUP", "COMPARE", "CHECKLIST", "EXPLAIN"
    query_type: str

    # Which specific regulation(s) the question is about. Set by the Router.
    # e.g., ["SR 11-7"] or ["SR 11-7", "NIST AI RMF"] or [] if general
    target_regulations: list[str]

    # The relevant document chunks found by the Retriever agent.
    # Each item is a LangChain Document object with .page_content and .metadata
    retrieved_docs: list

    # The generated answer. Set by the Synthesizer agent.
    answer: str

    # Verification result from the Compliance Checker agent.
    # Contains: {"claims": [...], "confidence": 0.0-1.0, "summary": "..."}
    verification: dict

    # How many times we've retried retrieval (max 2).
    # If confidence is low, we retry with different parameters.
    retry_count: int
