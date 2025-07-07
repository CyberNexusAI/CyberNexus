import os
import asyncio
from typing import Optional
from app.models.file import FileReadResult
from app.core.exceptions import AppException, ResourceNotFoundException, BadRequestException

class FileService:
    """File Operation Service"""

    async def read_file(self, file: str, start_line: Optional[int] = None, 
                 end_line: Optional[int] = None, sudo: bool = False) -> FileReadResult:
        # Check if file exists
        if not os.path.exists(file) and not sudo:
            raise ResourceNotFoundException(f"File does not exist: {file}")
        
        try:
            content = ""
            
            # Read with sudo
            if sudo:
                command = f"sudo cat '{file}'"
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    raise BadRequestException(f"Failed to read file: {stderr.decode()}")
                
                content = stdout.decode('utf-8')
            else:
                # Asynchronously read file
                def read_file_async():
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            return f.read()
                    except Exception as e:
                        raise AppException(message=f"Failed to read file: {str(e)}")
                
                # Execute IO operation in thread pool
                content = await asyncio.to_thread(read_file_async)
            
            # Process line range
            if start_line is not None or end_line is not None:
                lines = content.splitlines()
                start = start_line if start_line is not None else 0
                end = end_line if end_line is not None else len(lines)
                content = '\n'.join(lines[start:end])
            
            return FileReadResult(
                content=content,
                file=file
            )
        except Exception as e:
            if isinstance(e, BadRequestException) or isinstance(e, ResourceNotFoundException):
                raise e
            raise AppException(message=f"Failed to read file: {str(e)}")
        

file_service = FileService()