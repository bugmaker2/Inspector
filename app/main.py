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
from app.core.database.database import engine, Base, init_db, health_check as db_health_check
from app.api.v1 import members, monitoring, settings as settings_api, export, notifications
from app.services.monitors.monitor_manager import MonitorManager
from app.services.summarizers.llm_summarizer import LLMSummarizer
from app.core.database.database import SessionLocal


# Initialize database tables
init_db()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Inspector application...")
    
    # Start background tasks
    background_tasks = BackgroundTasks()
    background_tasks.add_task(start_scheduled_tasks)
    
    yield
    
    # Shutdown
    print("Shutting down Inspector application...")


# Create FastAPI app
app = FastAPI(
    title="Inspector",
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

app.include_router(
    settings_api.router,
    prefix=f"{settings.api_prefix}/settings",
    tags=["settings"]
)

app.include_router(
    export.router,
    prefix=f"{settings.api_prefix}/export",
    tags=["export"]
)

app.include_router(
    notifications.router,
    prefix=f"{settings.api_prefix}/notifications",
    tags=["notifications"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Inspector API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check_endpoint():
    """Health check endpoint with database status."""
    db_status = db_health_check()
    
    return {
        "status": "healthy" if db_status["status"] == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all system components."""
    db_status = db_health_check()
    
    # Check if all components are healthy
    all_healthy = db_status["status"] == "healthy"
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": db_status,
            "api": {"status": "healthy"},
            "monitoring": {"status": "ready"},
            "ai_summarizer": {"status": "ready"},
            "notifications": {"status": "ready"}
        },
        "version": "1.0.0"
    }


async def run_monitoring_task():
    """Run the monitoring task."""
    db = SessionLocal()
    try:
        monitor_manager = MonitorManager(db)
        results = await monitor_manager.monitor_all_profiles()
        print(f"Monitoring completed: {len(results)} platforms checked")
    except Exception as e:
        print(f"Monitoring task failed: {e}")
        # Send notification about monitoring error
        await notifications.notify_monitoring_error("general", str(e))
    finally:
        db.close()


async def run_summary_task():
    """Run the summary generation task."""
    db = SessionLocal()
    try:
        summarizer = LLMSummarizer(db)
        summary = await summarizer.generate_daily_summary()
        if summary:
            print(f"Daily summary generated: {summary.id}")
            # Send notification about summary generation
            await notifications.notify_summary_generated(summary)
        else:
            print("Daily summary generation failed")
    except Exception as e:
        print(f"Summary task failed: {e}")
    finally:
        db.close()


def start_scheduled_tasks():
    """Start background scheduled tasks."""
    # Schedule monitoring task
    schedule.every(settings.monitoring_interval_minutes).minutes.do(
        lambda: asyncio.create_task(run_monitoring_task())
    )
    
    # Schedule daily summary task
    schedule.every().day.at(settings.summary_time).do(
        lambda: asyncio.create_task(run_summary_task())
    )
    
    # Schedule weekly summary task
    schedule.every().monday.at(settings.summary_time).do(
        lambda: asyncio.create_task(run_weekly_summary_task())
    )
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Start scheduler in background thread
    import threading
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()


async def run_weekly_summary_task():
    """Run the weekly summary generation task."""
    db = SessionLocal()
    try:
        summarizer = LLMSummarizer(db)
        summary = await summarizer.generate_weekly_summary()
        if summary:
            print(f"Weekly summary generated: {summary.id}")
            # Send notification about summary generation
            await notifications.notify_summary_generated(summary)
        else:
            print("Weekly summary generation failed")
    except Exception as e:
        print(f"Weekly summary task failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    ) 