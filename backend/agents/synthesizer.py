"""
Synthesizer Agent — generates an answer from retrieved documents.

Takes the document chunks found by the Retriever and writes a coherent,
well-cited answer. The response style adapts based on the query type:
- LOOKUP  -> concise, direct answer
- COMPARE -> structured comparison with bullet points
- CHECKLIST -> numbered requirements list
- EXPLAIN -> thorough explanation
"""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from agents.state import AgentState

load_dotenv()

# We use gpt-4o here (not mini) because answer quality matters.
# This is the user-facing output — it needs to be accurate and well-written.
_llm = None


def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return _llm

SYSTEM_PROMPT = """You are a regulatory compliance expert specializing in AI and model risk management.

Your task: Answer the user's question using ONLY the provided source documents.

Rules:
1. ONLY use information from the provided sources. Never add external knowledge.
2. Include inline citations in the format [Source: Regulation Name, Page X].
3. If the sources don't contain enough information to fully answer, explicitly state what is missing.
4. Be precise — regulatory guidance requires accuracy.

Style guidance based on question type:
- LOOKUP: Be concise and direct. Get to the point quickly.
- COMPARE: Use a structured format. Compare point by point.
- CHECKLIST: Return a numbered list of requirements or steps.
- EXPLAIN: Provide a clear, thorough explanation. Define key terms."""

USER_PROMPT = """Question type: {query_type}

Source documents:
{context}

Question: {query}

Provide your answer with inline citations."""


def format_context(docs: list) -> str:
    """
    Format the retrieved documents into a string the LLM can read.

    Each chunk becomes a labeled block like:
      [Source: SR 11-7 | Page 12]
      The actual text content of the chunk...

    This format makes it easy for the LLM to cite specific sources.
    """
    formatted = []
    for doc in docs:
        regulation = doc.metadata.get("regulation", "Unknown")
        page = doc.metadata.get("page", "?")
        text = doc.page_content

        formatted.append(f"[Source: {regulation} | Page {page}]\n{text}")

    return "\n\n---\n\n".join(formatted)


def synthesizer_agent(state: AgentState) -> AgentState:
    """
    Generate an answer with citations from the retrieved documents.

    Input state needs: query, query_type, retrieved_docs
    Output state adds: answer
    """
    query = state["query"]
    query_type = state["query_type"]
    docs = state["retrieved_docs"]

    # Format retrieved chunks into a readable context string
    context = format_context(docs)

    # Build the prompt
    user_message = USER_PROMPT.format(
        query_type=query_type,
        context=context,
        query=query,
    )

    # Call the LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    response = get_llm().invoke(messages)
    state["answer"] = response.content

    return state
