from pydantic import BaseModel, Field


class FileReadResult(BaseModel):
    """File read result"""
    content: str = Field(..., description="File content")
    file: str = Field(..., description="Path of the read file")