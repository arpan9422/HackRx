from langchain.text_splitter import RecursiveCharacterTextSplitter
from semantic_splitter import SemanticSplitter
from sentence_transformers import SentenceTransformer

def chunk_text(text: str, source_name="document.pdf", use_semantic=True) -> list[str]:
    """
    Chunk large text using semantic splitting (if enabled), else use recursive splitter.
    """
    # Normalize & strip text
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()

    chunks = []

    if use_semantic:
        try:
            model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and lightweight
            splitter = SemanticSplitter(model.encode, chunk_size=800)
            chunks = splitter.split_text(
                  text="This is a long document. We want to semantically split it.",
                  chunk_token_length=128,
                  buffer_token_length=20
                )
        except Exception as e:
            print(f"⚠️ Semantic splitting failed, falling back: {e}")

    # Fallback: RecursiveCharacterTextSplitter (LangChain)
    if not chunks:
        print("🔁 Using RecursiveCharacterTextSplitter...")
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = recursive_splitter.split_text(text)

    # Add metadata
    enhanced_chunks = [
        f"(Source: {source_name}, Chunk {i+1})\n\n{chunk.strip()}"
        for i, chunk in enumerate(chunks)
        if chunk.strip()
    ]

    return enhanced_chunks
