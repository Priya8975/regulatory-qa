"""
Retriever Agent — searches the vector store for relevant passages.

This agent uses the query type (from the Router) to decide HOW to search:
- LOOKUP queries filter to a specific regulation for focused results
- COMPARE queries search broadly across all regulations
- CHECKLIST/EXPLAIN queries do a general search

The retrieved documents are passed to the Synthesizer to generate an answer.
"""

from agents.state import AgentState
from ingestion.retriever import similarity_search


def retriever_agent(state: AgentState) -> AgentState:
    """
    Retrieve relevant regulatory passages from ChromaDB.

    Input state needs: query, query_type, target_regulations
    Output state adds: retrieved_docs, increments retry_count
    """
    query = state["query"]
    query_type = state["query_type"]
    target_regulations = state["target_regulations"]
    retry_count = state.get("retry_count", 0)

    # Choose retrieval strategy based on query type
    if query_type == "LOOKUP" and len(target_regulations) == 1:
        # LOOKUP with a specific regulation mentioned:
        # Filter to just that regulation for precise results.
        # Example: "What does SR 11-7 say about validation?"
        #   -> Only search SR 11-7 chunks, return 5 results
        results = similarity_search(
            query=query,
            k=5,
            filter_dict={"regulation": target_regulations[0]},
        )

    elif query_type == "COMPARE" and len(target_regulations) >= 2:
        # COMPARE with specific regulations mentioned:
        # Search EACH regulation separately so both sides are represented.
        # Without this, one regulation can dominate the results.
        # Example: "How do SR 11-7 and NIST differ?"
        #   -> Get 5 chunks from SR 11-7 + 5 chunks from NIST
        results = []
        per_regulation = max(5, 10 // len(target_regulations))
        for reg in target_regulations:
            reg_results = similarity_search(
                query=query,
                k=per_regulation,
                filter_dict={"regulation": reg},
            )
            results.extend(reg_results)

    elif query_type == "COMPARE":
        # COMPARE without specific regulations: broad search
        results = similarity_search(query=query, k=10)

    else:
        # CHECKLIST, EXPLAIN, or LOOKUP without a specific regulation:
        # General search, moderate number of results.
        results = similarity_search(query=query, k=7)

    # On retry (if compliance checker found low confidence),
    # broaden the search to get more diverse results.
    if retry_count > 0 and len(results) < 3:
        results = similarity_search(query=query, k=10)

    state["retrieved_docs"] = results
    state["retry_count"] = retry_count + 1

    return state
