from pydantic import BaseModel, Field
from typing import Optional


class FileReadRequest(BaseModel):
    """File read request"""
    file: str = Field(..., description="Absolute file path")
    start_line: Optional[int] = Field(None, description="Start line (0-based)")
    end_line: Optional[int] = Field(None, description="End line (not inclusive)")
    sudo: Optional[bool] = Field(False, description="Whether to use sudo privileges")