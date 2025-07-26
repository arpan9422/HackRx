from fastapi import FastAPI
from app.routes.query_router import router as query_router
from app.routes.upload_router import router as upload_router

app = FastAPI()

# Register routes
app.include_router(upload_router, prefix="/upload")
app.include_router(query_router, prefix="/ask")  # 👈 Add this line

@app.get("/")
def root():
    return {"message": "RAG API running"}
