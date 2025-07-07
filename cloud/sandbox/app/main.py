from fastapi import FastAPI
import logging
import sys
from app.core.config import settings
from app.api.router import api_router

# Configure logging
def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    # Get root logger
    root_logger = logging.getLogger()
    
    # Set root log level
    log_level = getattr(logging, settings.LOG_LEVEL)
    root_logger.setLevel(log_level)
    
    # Log setup completion
    logging.info("Sandbox logging system initialized with level: %s", settings.LOG_LEVEL)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    version="1.0.0",  # The version of the API.
)

logger.info("Sandbox API server starting")

# Register routes
app.include_router(api_router, prefix="/api/v1")

logger.info("Sandbox API routes registered and server ready")