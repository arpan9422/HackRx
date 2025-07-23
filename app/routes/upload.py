from fastapi import APIRouter

upload_router = APIRouter()

@upload_router.get("/")
async def test_upload():
    return {"message": "Upload router working"}
