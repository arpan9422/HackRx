import os
import uuid
import asyncio
import concurrent.futures
from dotenv import load_dotenv
from app.utils.pinecone_client import index  # Pinecone client for storing vectors

# Load environment variables
load_dotenv()

# Use MiniLM model if enabled in .env
USE_MINILM = os.getenv("USE_MINILM", "true").lower() == "true"
if USE_MINILM:
    # ✅ Using MiniLM model for generating embeddings
    from sentence_transformers import SentenceTransformer
    minilm_model = SentenceTransformer("all-MiniLM-L6-v2")
else:
    # ❌ Gemini Embedding commented out for now
    # from google.generativeai import EmbeddingModel, configure
    # configure(api_key=os.getenv("GEMINI_API_KEY"))
    # model = EmbeddingModel(model_name="models/embedding-001")
    pass

# -----------------------------------------------
# Get embedding for a single chunk (synchronously)
# -----------------------------------------------
def get_embedding(text: str) -> list[float]:
    return minilm_model.encode(text).tolist()

# --------------------------------------------------------
# Wrap get_embedding to run it asynchronously using thread
# --------------------------------------------------------
async def embed_chunk_async(executor, chunk):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, get_embedding, chunk)

# -----------------------------------------------------------
# Main async function: generate embeddings & store in Pinecone
# -----------------------------------------------------------
async def embed_chunks_async(chunks, source_name, metadata_info, batch_size=10):
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]  # Remove empty chunks
    executor = concurrent.futures.ThreadPoolExecutor()

    # Step 1: Get embeddings for all chunks concurrently
    tasks = [embed_chunk_async(executor, chunk) for chunk in chunks]
    embeddings = await asyncio.gather(*tasks)

    # Step 2: Prepare Pinecone metadata with additional PDF info
    pinecone_data = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        metadata = {
            "text": chunk,
            "file_name": os.path.basename(source_name),
            "loc.lines.from": i * 10 + 1,
            "loc.lines.to": i * 10 + 10,
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

        pinecone_data.append({
            "id": str(uuid.uuid4()),         # Unique ID for this embedding
            "values": embedding,             # Embedding vector
            "metadata": metadata             # Metadata for this chunk
        })

    # Step 3: Insert data into Pinecone in batches using threads
    with concurrent.futures.ThreadPoolExecutor() as thread_pool:
        futures = []
        for i in range(0, len(pinecone_data), batch_size):
            batch = pinecone_data[i:i+batch_size]
            futures.append(thread_pool.submit(index.upsert, batch))  # Upsert to Pinecone
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                print(f"✅ Batch {i+1}/{len(futures)} inserted")
            except Exception as e:
                print(f"❌ Batch {i+1} failed: {e}")

# ---------------------------------------------
# Entrypoint to call from other parts of system
# ---------------------------------------------
async def embed_chunks(chunks, source_name="/Users/shubhamrade/Desktop/Bajaj/BAJHLIP23020V012223.pdf", metadata_info={}):
   await embed_chunks_async(chunks, source_name, metadata_info)
