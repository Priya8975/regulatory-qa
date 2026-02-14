"""
LangGraph workflow — wires all agents together into a pipeline.

The flow:
  Router -> Retriever -> Synthesizer -> Compliance Checker
                ^                              |
                |______ retry if confidence < 0.7 (max 2 retries)

This file is the "main brain" of the system. It:
1. Defines the graph (which agent connects to which)
2. Adds a conditional retry loop for low-confidence answers
3. Provides the ask_question() function that the API will call
"""

from dotenv import load_dotenv
from langgraph.graph import StateGraph, END

from agents.state import AgentState
from agents.router import router_agent
from agents.retriever import retriever_agent
from agents.synthesizer import synthesizer_agent
from agents.compliance_checker import compliance_checker_agent

load_dotenv()


def should_retry(state: AgentState) -> str:
    """
    Decide whether to retry retrieval or finish.

    Called after the Compliance Checker. If confidence is below 0.7
    and we haven't retried too many times, go back to the Retriever
    for another attempt with potentially different results.

    Returns:
        "retry" -> go back to retriever
        "end"   -> we're done, return the answer
    """
    confidence = state.get("verification", {}).get("confidence", 1.0)
    retry_count = state.get("retry_count", 0)

    if confidence < 0.7 and retry_count <= 2:
        return "retry"
    return "end"


def build_graph() -> StateGraph:
    """
    Build and compile the LangGraph workflow.

    The graph has 4 nodes (one per agent) and edges connecting them.
    The key feature is the conditional edge after compliance_checker:
    it either ends or loops back to the retriever.
    """
    workflow = StateGraph(AgentState)

    # Add each agent as a node in the graph
    workflow.add_node("router", router_agent)
    workflow.add_node("retriever", retriever_agent)
    workflow.add_node("synthesizer", synthesizer_agent)
    workflow.add_node("compliance_checker", compliance_checker_agent)

    # Define the flow: router -> retriever -> synthesizer -> compliance_checker
    workflow.set_entry_point("router")
    workflow.add_edge("router", "retriever")
    workflow.add_edge("retriever", "synthesizer")
    workflow.add_edge("synthesizer", "compliance_checker")

    # Conditional edge: retry or finish
    workflow.add_conditional_edges(
        "compliance_checker",
        should_retry,
        {"retry": "retriever", "end": END},
    )

    return workflow.compile()


# Compile the graph once at import time (so it's ready to use)
app = build_graph()


def format_sources(docs: list) -> list[dict]:
    """Convert LangChain Document objects into simple dicts for the API response."""
    sources = []
    for doc in docs:
        sources.append({
            "regulation": doc.metadata.get("regulation", "Unknown"),
            "page": doc.metadata.get("page", 0),
            "content": doc.page_content[:300],  # Truncate for readability
        })
    return sources


def ask_question(query: str) -> dict:
    """
    Main entry point — ask a regulatory question and get an answer.

    This is what the FastAPI endpoint will call. It:
    1. Creates the initial state with the user's question
    2. Runs it through the full agent pipeline
    3. Returns a clean response dict

    Args:
        query: The user's question (e.g., "What does SR 11-7 require?")

    Returns:
        {
            "answer": "SR 11-7 requires...",
            "sources": [{"regulation": "SR 11-7", "page": 12, "content": "..."}],
            "confidence": 0.92,
            "query_type": "LOOKUP",
            "verification": {...}
        }
    """
    # Build the initial state — only query is set, everything else is empty
    initial_state = {
        "query": query,
        "query_type": "",
        "target_regulations": [],
        "retrieved_docs": [],
        "answer": "",
        "verification": {},
        "retry_count": 0,
    }

    # Run the full pipeline
    result = app.invoke(initial_state)

    # Package the response
    return {
        "answer": result["answer"],
        "sources": format_sources(result["retrieved_docs"]),
        "confidence": result.get("verification", {}).get("confidence", 0),
        "query_type": result["query_type"],
        "verification": result.get("verification", {}),
    }
