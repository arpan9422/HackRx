from fastapi import FastAPI
from routes.upload import upload_router

app = FastAPI()

app.include_router(upload_router, prefix="/upload")
