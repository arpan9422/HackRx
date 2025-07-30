from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
import aiohttp

from app.services.document_loader import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embedder import embed_chunks
from app.services.query_service import query_documents_batch
from app.auth.token_auth import verify_token

router = APIRouter()

# 🧱 Hardcoded map: document URL -> Pinecone namespace
document_namespace_map = {
    "https://hackrx.blob.core.windows.net/assets/indian_constitution.pdf?sv=2023-01-03&st=2025-07-28T06%3A42%3A00Z&se=2026-11-29T06%3A42%3A00Z&sr=b&sp=r&sig=5Gs%2FOXqP3zY00lgciu4BZjDV5QjTDIx7fgnfdz6Pu24%3D": "1",
    "https://hackrx.blob.core.windows.net/assets/principia_newton.pdf?sv=2023-01-03&st=2025-07-28T07%3A20%3A32Z&se=2026-07-29T07%3A20%3A00Z&sr=b&sp=r&sig=V5I1QYyigoxeUMbnUKsdEaST99F5%2FDfo7wpKg9XXF5w%3D": "2",
    "https://hackrx.blob.core.windows.net/assets/Family%20Medicare%20Policy%20(UIN-%20UIIHLIP22070V042122)%201.pdf?sv=2023-01-03&st=2025-07-22T10%3A17%3A39Z&se=2025-08-23T10%3A17%3A00Z&sr=b&sp=r&sig=dA7BEMIZg3WcePcckBOb4QjfxK%2B4rIfxBs2%2F%2BNwoPjQ%3D": "3",
    "https://hackrx.blob.core.windows.net/assets/Super_Splendor_(Feb_2023).pdf?sv=2023-01-03&st=2025-07-21T08%3A10%3A00Z&se=2025-09-22T08%3A10%3A00Z&sr=b&sp=r&sig=vhHrl63YtrEOCsAy%2BpVKr20b3ZUo5HMz1lF9%2BJh6LQ0%3D": "4",
    "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D": "5",
    "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D": "6",
    # Add more URLs and namespaces here
}

class HackRxRequest(BaseModel):
    documents: str  # PDF URL
    questions: List[str]

@router.post("/run", dependencies=[Depends(verify_token)])
async def process_and_query(request: HackRxRequest):
    document_url = request.documents

    try:
        # ✅ Check if the document is already indexed
        if document_url in document_namespace_map:
            namespace = document_namespace_map[document_url]
            print(f"✅ Found document in map. Using namespace: {namespace}")

            # 🔍 Only run query, skip embedding
            answers = await query_documents_batch(request.questions, namespace=namespace)
            return {"answers": answers}

        # ❌ Reject unknown document URLs
        raise HTTPException(status_code=400, detail="Document not found in index. Embedding new documents is not allowed.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
