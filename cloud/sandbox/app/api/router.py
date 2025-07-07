from fastapi import APIRouter
from app.api.v1 import file

api_router = APIRouter()
api_router.include_router(file.router, prefix="/file", tags=["file"])