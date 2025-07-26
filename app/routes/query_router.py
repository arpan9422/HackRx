from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.query_service import query_documents
from app.auth.token_auth import verify_token


router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query", dependencies=[Depends(verify_token)])
def query_route(req: QueryRequest):
    try:
        response = query_documents(req.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
