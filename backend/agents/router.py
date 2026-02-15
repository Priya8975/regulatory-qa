"""
Router Agent — classifies the user's question.

This is the first agent in the pipeline. It reads the user's question
and determines:
1. What TYPE of question it is (LOOKUP, COMPARE, CHECKLIST, EXPLAIN)
2. Which specific REGULATION(S) the question is about

This information helps the Retriever agent decide how to search.
"""

import logging

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.state import AgentState

logger = logging.getLogger(__name__)

load_dotenv()

# We use gpt-4o-mini for routing because:
# - Classification is a simple task, doesn't need the full gpt-4o
# - gpt-4o-mini is ~20x cheaper and much faster
# - Accuracy is more than sufficient for 4-way classification
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _llm

# All regulations we know about. Used to detect which ones are mentioned.
KNOWN_REGULATIONS = [
    "SR 11-7",
    "NIST AI RMF",
    "ISO 42001",
    "NAIC Model Bulletin",
    "Colorado SB21-169",
]

CLASSIFICATION_PROMPT = """You are a regulatory compliance query classifier.

Classify the following question into exactly ONE of these categories:

- LOOKUP: The user wants a specific fact or detail from one regulation.
  Example: "What does SR 11-7 say about model documentation?"

- COMPARE: The user wants to compare across multiple regulations.
  Example: "How do NIST AI RMF and SR 11-7 differ on risk assessment?"

- CHECKLIST: The user wants a list of requirements, steps, or action items.
  Example: "What do I need to comply with NAIC AI guidelines?"

- EXPLAIN: The user wants a concept or term explained.
  Example: "What is effective challenge in model validation?"

Question: {query}

Respond with ONLY the category name (LOOKUP, COMPARE, CHECKLIST, or EXPLAIN).
Nothing else."""


def detect_regulations(query: str) -> list[str]:
    """
    Simple keyword detection to find which regulations are mentioned.

    We check for variations of each regulation name. For example,
    "SR 11-7" might appear as "SR11-7", "SR 11-7", or "sr 11-7".

    Returns a list like ["SR 11-7"] or ["SR 11-7", "NIST AI RMF"].
    Empty list if no specific regulation is mentioned.
    """
    query_lower = query.lower()
    found = []

    # Map of keyword patterns -> regulation name
    patterns = {
        "SR 11-7": ["sr 11-7", "sr11-7", "sr1107", "sr 1107"],
        "NIST AI RMF": ["nist", "ai rmf", "ai 100-1", "ai100"],
        "ISO 42001": ["iso 42001", "iso42001"],
        "NAIC Model Bulletin": ["naic", "model bulletin"],
        "Colorado SB21-169": ["colorado", "sb21-169", "sb 21-169", "sb21169"],
    }

    for regulation, keywords in patterns.items():
        for keyword in keywords:
            if keyword in query_lower:
                found.append(regulation)
                break  # Found this regulation, move to next

    return found


def router_agent(state: AgentState) -> AgentState:
    """
    Classify the query and detect target regulations.

    Input state needs: query
    Output state adds: query_type, target_regulations
    """
    query = state["query"]

    # Step 1: Classify the query type using the LLM
    prompt = CLASSIFICATION_PROMPT.format(query=query)
    response = get_llm().invoke(prompt)
    query_type = response.content.strip().upper()

    # Validate — if the LLM returns something unexpected, default to EXPLAIN
    valid_types = {"LOOKUP", "COMPARE", "CHECKLIST", "EXPLAIN"}
    if query_type not in valid_types:
        logger.warning("LLM returned unexpected query type '%s', defaulting to EXPLAIN", query_type)
        query_type = "EXPLAIN"

    # Step 2: Detect which regulations are mentioned (no LLM needed, just keywords)
    target_regulations = detect_regulations(query)

    state["query_type"] = query_type
    state["target_regulations"] = target_regulations

    return state
