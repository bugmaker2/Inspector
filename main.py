"""Main entry point for Inspector Cursor application."""

import uvicorn
from app.core.config.settings import settings


def main():
    """Start the Inspector Cursor application."""
    print("Starting Inspector Cursor - Social Media Activity Monitor")
    print(f"API will be available at http://{settings.api_host}:{settings.api_port}")
    print(f"API documentation at http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
