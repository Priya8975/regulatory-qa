"""
Document ingestion pipeline.

This script:
1. Reads all PDF files from the data/ directory
2. Splits them into smaller text chunks (because LLMs have token limits)
3. Generates vector embeddings for each chunk (numerical representation of meaning)
4. Stores everything in ChromaDB (a local vector database) for fast semantic search
"""

import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

# Paths
# Go up two levels from this file: ingestion/ -> backend/ -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_DIR = PROJECT_ROOT / "backend" / "chroma_db"

# Maps PDF filenames (lowercase) to a clean regulation name.
# When you add a new PDF, add an entry here so the system knows what regulation it belongs to.
REGULATION_MAP = {
    "sr1107": "SR 11-7",
    "sr11-7": "SR 11-7",
    "nist": "NIST AI RMF",
    "ai100": "NIST AI RMF",
    "iso42001": "ISO 42001",
    "iso_42001": "ISO 42001",
    "naic": "NAIC Model Bulletin",
    "colorado": "Colorado SB21-169",
    "sb21": "Colorado SB21-169",
}


def detect_regulation_name(filename: str) -> str:
    """
    Given a PDF filename, figure out which regulation it belongs to.

    How it works:
    - Converts filename to lowercase
    - Checks if any key from REGULATION_MAP appears in the filename
    - Returns the matched regulation name, or "Unknown" if no match

    Example:
        "SR1107a1.pdf" -> looks for "sr1107" in "sr1107a1.pdf" -> "SR 11-7"
        "NIST.AI.100-1.pdf" -> looks for "nist" in "nist.ai.100-1.pdf" -> "NIST AI RMF"
    """
    name_lower = filename.lower()
    for key, regulation in REGULATION_MAP.items():
        if key in name_lower:
            return regulation
    return "Unknown"


def load_pdfs(data_dir: Path) -> list:
    """
    Load all PDF files from the data directory.

    For each page in each PDF, we attach metadata:
    - regulation: which regulation this page belongs to (e.g., "SR 11-7")
    - source: the original filename
    - page: the page number

    This metadata is crucial later — it lets us filter search results
    by regulation and show users exactly where an answer came from.
    """
    all_docs = []
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        print("Please add regulatory PDF documents to the data/ directory.")
        sys.exit(1)

    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path.name}")
        regulation_name = detect_regulation_name(pdf_path.name)
        print(f"  -> Detected regulation: {regulation_name}")

        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()

        # Attach metadata to each page
        for page in pages:
            page.metadata["regulation"] = regulation_name
            page.metadata["source"] = pdf_path.name
            # PyPDFLoader already sets "page" in metadata (0-indexed)

        all_docs.extend(pages)
        print(f"  -> Loaded {len(pages)} pages")

    return all_docs


def chunk_documents(documents: list) -> list:
    """
    Split documents into smaller chunks for embedding.

    Why chunk?
    - LLMs have a limited context window (e.g., 8K-128K tokens)
    - Smaller chunks = more precise search results
    - We want to retrieve the *specific paragraph* that answers a question,
      not an entire 10-page section

    Settings:
    - chunk_size=800: ~200 tokens per chunk. Enough context to be useful,
      small enough for precise retrieval.
    - chunk_overlap=200: Chunks overlap by 200 chars so we don't lose context
      at chunk boundaries. If a key sentence spans two chunks, both will have it.
    - separators: We prefer splitting at paragraph breaks (\n\n), then line breaks (\n),
      then sentences (". "), then words (" "). This keeps logical units together.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " "],
    )

    chunks = splitter.split_documents(documents)
    return chunks


def create_vector_store(chunks: list) -> Chroma:
    """
    Generate embeddings and store in ChromaDB.

    What are embeddings?
    - Each text chunk gets converted into a vector (list of ~1536 numbers)
    - These vectors capture the *meaning* of the text
    - Similar meanings = vectors that are close together in space
    - When a user asks a question, we embed the question too, then find the
      closest chunk vectors = most relevant passages

    We use OpenAI's text-embedding-3-small model:
    - Fast, cheap, and good quality
    - Returns 1536-dimensional vectors

    ChromaDB stores these vectors locally on disk so we don't have to
    re-generate embeddings every time.
    """
    print(f"\nCreating vector store at: {CHROMA_DIR}")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name="regulations",
    )

    return vectorstore


def main():
    """Run the full ingestion pipeline."""
    print("=" * 60)
    print("  Regulatory Document Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load PDFs
    print(f"\n[Step 1/3] Loading PDFs from {DATA_DIR}...")
    documents = load_pdfs(DATA_DIR)
    print(f"\nTotal pages loaded: {len(documents)}")

    # Step 2: Chunk documents
    print("\n[Step 2/3] Splitting into chunks...")
    chunks = chunk_documents(documents)
    print(f"Total chunks created: {len(chunks)}")

    # Show a sample chunk so you can verify it looks right
    if chunks:
        sample = chunks[0]
        print("\nSample chunk:")
        print(f"  Regulation: {sample.metadata.get('regulation')}")
        print(f"  Source: {sample.metadata.get('source')}")
        print(f"  Page: {sample.metadata.get('page')}")
        print(f"  Text preview: {sample.page_content[:150]}...")

    # Step 3: Create vector store
    print("\n[Step 3/3] Creating vector store and generating embeddings...")
    vectorstore = create_vector_store(chunks)
    print("Vector store created successfully!")

    # Verify: run a test query
    print(f"\n{'=' * 60}")
    print("  Verification: Running test query")
    print(f"{'=' * 60}")
    test_query = "model risk management"
    results = vectorstore.similarity_search(test_query, k=3)
    print(f'Query: "{test_query}"')
    print(f"Top {len(results)} results:")
    for i, doc in enumerate(results):
        print(f"\n  Result {i + 1}:")
        print(f"    Regulation: {doc.metadata.get('regulation')}")
        print(f"    Page: {doc.metadata.get('page')}")
        print(f"    Preview: {doc.page_content[:120]}...")

    print("\nIngestion complete!")


if __name__ == "__main__":
    main()
