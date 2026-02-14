"""
Vector store retrieval utilities.

This module provides functions to search the ChromaDB vector store.
The agents (Router, Retriever, etc.) will use these functions to find
relevant regulatory passages when answering user questions.

Two main ways to search:
1. get_retriever() - Returns a LangChain Retriever object (used in chains)
2. similarity_search() - Direct search, returns a list of Document objects
"""

from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# Path to the persisted ChromaDB directory
CHROMA_DIR = Path(__file__).resolve().parent.parent / "chroma_db"


def get_vectorstore() -> Chroma:
    """
    Load and return the persisted ChromaDB vector store.

    This connects to the vector store we created during ingestion.
    It does NOT re-create embeddings — it just loads what's already on disk.
    """
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        collection_name="regulations",
    )

    return vectorstore


def get_retriever(k: int = 7, filter_dict: dict | None = None):
    """
    Return a LangChain Retriever object.

    Parameters:
        k: Number of results to return (default 7)
        filter_dict: Optional metadata filter, e.g., {"regulation": "SR 11-7"}
                     This restricts search to chunks from that regulation only.

    Returns:
        A VectorStoreRetriever that can be used in LangChain chains.

    Example:
        # Search across all regulations
        retriever = get_retriever(k=5)

        # Search only within SR 11-7
        retriever = get_retriever(k=5, filter_dict={"regulation": "SR 11-7"})
    """
    vectorstore = get_vectorstore()

    search_kwargs = {"k": k}
    if filter_dict:
        search_kwargs["filter"] = filter_dict

    return vectorstore.as_retriever(search_kwargs=search_kwargs)


def similarity_search(
    query: str,
    k: int = 7,
    filter_dict: dict | None = None,
) -> list:
    """
    Direct similarity search — returns the most relevant document chunks.

    This is a simpler alternative to get_retriever() when you just want
    the results directly without wrapping in a chain.

    Parameters:
        query: The search query (e.g., "model validation requirements")
        k: Number of results to return
        filter_dict: Optional metadata filter

    Returns:
        List of Document objects, each with:
        - page_content: the text of the chunk
        - metadata: dict with "regulation", "source", "page" keys
    """
    vectorstore = get_vectorstore()

    if filter_dict:
        results = vectorstore.similarity_search(query, k=k, filter=filter_dict)
    else:
        results = vectorstore.similarity_search(query, k=k)

    return results
