"""Main FastAPI application."""

import asyncio
import schedule
import time
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config.settings import settings
from app.core.database.database import engine, Base
from app.api.v1 import members, monitoring
from app.services.monitors.monitor_manager import MonitorManager
from app.services.summarizers.llm_summarizer import LLMSummarizer
from app.core.database.database import SessionLocal


# Create database tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Inspector Cursor application...")
    
    # Start background tasks
    background_tasks = BackgroundTasks()
    background_tasks.add_task(start_scheduled_tasks)
    
    yield
    
    # Shutdown
    print("Shutting down Inspector Cursor application...")


# Create FastAPI app
app = FastAPI(
    title="Inspector Cursor",
    description="Social media activity monitoring and summarization service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(
    members.router,
    prefix=f"{settings.api_prefix}/members",
    tags=["members"]
)

app.include_router(
    monitoring.router,
    prefix=f"{settings.api_prefix}/monitoring",
    tags=["monitoring"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Inspector Cursor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


async def run_monitoring_task():
    """Run the monitoring task."""
    db = SessionLocal()
    try:
        monitor_manager = MonitorManager(db)
        result = await monitor_manager.run_scheduled_monitoring()
        print(f"Monitoring task completed: {result}")
    except Exception as e:
        print(f"Monitoring task failed: {e}")
    finally:
        db.close()


async def run_summary_task():
    """Run the summary generation task."""
    db = SessionLocal()
    try:
        summarizer = LLMSummarizer(db)
        if summarizer.can_summarize():
            # Generate daily summary
            summary = await summarizer.generate_daily_summary()
            if summary:
                print(f"Daily summary generated: {summary.title}")
            else:
                print("No activities found for daily summary")
        else:
            print("LLM summarization not available")
    except Exception as e:
        print(f"Summary task failed: {e}")
    finally:
        db.close()


def start_scheduled_tasks():
    """Start scheduled background tasks."""
    print("Starting scheduled tasks...")
    
    # Schedule monitoring task
    schedule.every(settings.monitoring_interval_minutes).minutes.do(
        lambda: asyncio.create_task(run_monitoring_task())
    )
    
    # Schedule daily summary task (run at 9 AM daily)
    schedule.every().day.at("09:00").do(
        lambda: asyncio.create_task(run_summary_task())
    )
    
    # Schedule weekly summary task (run on Monday at 9 AM)
    schedule.every().monday.at("09:00").do(
        lambda: asyncio.create_task(run_weekly_summary_task())
    )
    
    # Run the scheduler in a separate thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    print("Scheduled tasks started")


async def run_weekly_summary_task():
    """Run the weekly summary generation task."""
    db = SessionLocal()
    try:
        summarizer = LLMSummarizer(db)
        if summarizer.can_summarize():
            # Generate weekly summary
            summary = await summarizer.generate_weekly_summary()
            if summary:
                print(f"Weekly summary generated: {summary.title}")
            else:
                print("No activities found for weekly summary")
        else:
            print("LLM summarization not available")
    except Exception as e:
        print(f"Weekly summary task failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    ) 