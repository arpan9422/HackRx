from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from app.services.document_loader import extract_text_from_pdf
from app.services.chunker import chunk_text
from app.services.embedder import embed_chunks
from app.services.query_service import query_documents
from app.services.query_service import query_documents_batch
from app.auth.token_auth import verify_token

router = APIRouter()

class HackRxRequest(BaseModel):
    documents: str  # PDF URL
    questions: List[str]

@router.post("/run", dependencies=[Depends(verify_token)])
async def process_and_query(request: HackRxRequest):
    try:
        # Step 1: Download PDF
        async with aiohttp.ClientSession() as session:
            async with session.get(request.documents) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to download document")
                document_bytes = await resp.read()

        # Step 2: Extract text
        text = extract_text_from_pdf(document_bytes)

        # Step 3: Chunk it
        chunks = chunk_text(text)

        # Step 4: Embed
        await embed_chunks(chunks)

        # Step 5: Query for answers (same as query_router)
        try:
            answers = await query_documents_batch(request.questions)
            return {"answer":answers}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")