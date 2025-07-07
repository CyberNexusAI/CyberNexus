from fastapi import APIRouter
from app.schemas.file import FileReadRequest
from app.schemas.response import Response
from app.services.file import file_service

router = APIRouter()

@router.post("/read", response_model=Response)
async def read_file(request: FileReadRequest):
    result = await file_service.read_file(
        file=request.file,
        start_line=request.start_line,
        end_line=request.end_line,
        sudo=request.sudo
    )
    
    # Construct response
    return Response(
        success=True,
        message="File read successfully",
        data=result.model_dump()
    )