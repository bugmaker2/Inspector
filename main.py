"""Main application entry point."""

import logging
from app.main import app
from app.core.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file) if settings.log_file else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Inspector - Social Media Activity Monitor")
    logger.info(f"API will be available at http://{settings.api_host}:{settings.api_port}")
    logger.info(f"API documentation at http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
