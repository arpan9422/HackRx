from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.query_service import query_documents

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def query_route(req: QueryRequest):
    try:
        response = query_documents(req.query)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
