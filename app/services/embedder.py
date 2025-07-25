import os
import uuid
from dotenv import load_dotenv
from app.utils.pinecone_client import index

load_dotenv()

USE_MINILM = os.getenv("USE_MINILM", "true").lower() == "true"

# --------------------------
# SentenceTransformer MiniLM (local, fast, free)
# --------------------------
if USE_MINILM:
    from sentence_transformers import SentenceTransformer
    minilm_model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------
# Gemini Embeddings (remote, requires GEMINI_API_KEY)
# --------------------------
# else:
#     import google.generativeai as genai
#     api_key = os.getenv("GEMINI_API_KEY")
#     if not api_key:
#         raise EnvironmentError("GEMINI_API_KEY not set in .env")
#     genai.configure(api_key=api_key)

def get_embedding(text: str) -> list[float]:
    if USE_MINILM:
        return minilm_model.encode(text).tolist()
    else:
        # Uncomment below to use Gemini embeddings
        # res = genai.embed_content(
        #     model="models/embedding-001",
        #     content=text,
        #     task_type="retrieval_document"
        # )
        # return res["embedding"]
        raise NotImplementedError("Gemini embedding is currently commented out. Set USE_MINILM=true or uncomment Gemini code.")

def embed_chunks(
    chunks: list[str],
    source_name="/path/to/file.pdf",
    metadata_info: dict = {}
):
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue

        embedding = get_embedding(chunk)
        if embedding:
            from_line = i * 10 + 1
            to_line = from_line + 9

            metadata = {
                "text": chunk,
                "file_name": os.path.basename(source_name),
                "loc.lines.from": from_line,
                "loc.lines.to": to_line,
                "blobType": "application/pdf",
                "pdf.info.Author": metadata_info.get("author", "Unknown"),
                "pdf.info.CreationDate": metadata_info.get("creation_date", "Unknown"),
                "pdf.info.Creator": metadata_info.get("creator", "Unknown"),
                "source": metadata_info.get("source", "unknown"),
                "page_number": metadata_info.get("page_number", i + 1),
                "document_type": metadata_info.get("document_type", "unknown"),
                "language": metadata_info.get("language", "en"),
                "doc_version": metadata_info.get("doc_version", "v1.0"),
                "chunk_index": i
            }

            try:
                index.upsert([
                    {
                        "id": str(uuid.uuid4()),
                        "values": embedding,
                        "metadata": metadata
                    }
                ])
                print(f"✅ Stored chunk {i+1}/{len(chunks)}")
            except Exception as e:
                print(f"❌ Upsert failed on chunk {i+1}: {e}")
